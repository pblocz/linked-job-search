from datetime import datetime
import json
from typing import Sequence
from dataclasses import dataclass
import azure.functions as func
import logging

# app = func.FunctionApp(http_auth_level=func.AuthLevel.FUNCTION)
import azure.functions as func
import azure.durable_functions as df
from dataclasses_json import dataclass_json

from jobsearch.linkedin import LinkedInProcessing, load_cookies
from jobsearch.models import JobInfo, LinkedinSearchLoad
from jobsearch.openai import job_summary_openai
from jobsearch.persistance import StorageLayer
from function.job_search_entity import JobSearchWatermark

app = df.DFApp(http_auth_level=func.AuthLevel.ANONYMOUS)


# An HTTP-Triggered Function with a Durable Functions Client binding
@app.route(route="orchestrators")
@app.durable_client_input(client_name="client")
async def http_start_job_search(
    req: func.HttpRequest, client: df.DurableOrchestrationClient
):
    # function_name = req.route_params.get('functionName')
    keywords = "Senior Data Scientist"
    instance_id = await client.start_new("job_search_orchestrator", None, keywords)

    keywords = "Senior Data Engineer"
    instance_id = await client.start_new("job_search_orchestrator", None, keywords)

    response = await client.wait_for_completion_or_create_check_status_response(
        req, instance_id
    )
    return response


@dataclass_json
@dataclass
class SearchParam:
    keywords: str
    listed_offset: int


# Orchestrator
@app.orchestration_trigger(context_name="context")
def job_search_orchestrator(context: df.DurableOrchestrationContext):
    keywords = context.get_input()
    logging.warn(keywords)

    current_time: JobSearchWatermark = yield context.call_activity("current_time")

    entityId = df.EntityId("JobSearchWatermark", keywords)
    entity = yield context.call_entity(entityId, "get")
    prev_time: JobSearchWatermark = JobSearchWatermark.from_json(entity["__data__"])

    diff = (current_time.value - prev_time.value).total_seconds()


    # Search for jobs
    raw_search_results: LinkedinSearchLoad = yield context.call_activity(
        "search", SearchParam(keywords, diff)
    )

    # Store in cosmos
    yield context.call_activity("persists_query_in_cosmos", raw_search_results)

    # Run processing for each job result
    tasks = [
        context.call_sub_orchestrator("job_info_orchestrator", result)
        for result in raw_search_results.jobs_reply
    ]
    job_infos: Sequence[JobInfo] = yield context.task_all(tasks)

    # Update timestamp
    entity = yield context.call_entity(entityId, "set", current_time)

    return job_infos


@app.orchestration_trigger(context_name="context")
def job_info_orchestrator(context: df.DurableOrchestrationContext):
    job = context.get_input()

    # Check if this job already run
    job_id = LinkedInProcessing.get_id_from_job(job)
    entity = df.EntityId("JobProcessed", job_id)
    has_run = yield context.call_entity(entity, "get")
    if has_run:
        return None

    # Process job
    job_info = yield context.call_activity("query_info", job)
    yield context.call_activity("persist_job_info", JobInfo.from_dict(job_info))

    # Set it as run
    yield context.call_entity(entity, "set")

    return job_info


@app.activity_trigger(input_name="nothing")
def current_time(nothing):
    return JobSearchWatermark(datetime.now())


# Activity
@app.activity_trigger(input_name="query")
def search(query: SearchParam):
    logging.info(f"running query {query}")
    cookies = load_cookies()
    api = LinkedInProcessing(cookies)

    load_time = datetime.now()
    listed_offset_seconds = query.listed_offset
    jobs_reply = api.search_remote_jobs(
        query.keywords, listed_offset_seconds=listed_offset_seconds
    )

    search_load = LinkedinSearchLoad(
        loadtime=load_time,
        keywords=query.keywords,
        listed_offset_seconds=listed_offset_seconds,
        jobs_reply=jobs_reply,
    )
    logging.info(f"query retuned {len(jobs_reply)} results")

    storage = StorageLayer()
    storage.persist_on_storage(
        "raw/job_searches/" + search_load.get_path_part(),
        search_load.get_file_name(),
        search_load,
    )

    return search_load


@app.activity_trigger(input_name="input")
@app.cosmos_db_output(
    arg_name="cosmos",
    database_name="linkedinjobs",
    container_name="query",
    partition_key="/query",
    create_if_not_exists=True,
    connection="CosmosConnection",
)
def persists_query_in_cosmos(
    input: LinkedinSearchLoad, cosmos: func.Out[func.DocumentList]
):
    query = input.keywords
    raw_jobs = input.jobs_reply

    messages = func.DocumentList()
    for job in raw_jobs:
        job_id = LinkedInProcessing.get_id_from_job(job)
        message = {"id": job_id, "query": query}
        messages.append(func.Document.from_dict(message))
    cosmos.set(messages)
    return ""


@app.activity_trigger(input_name="job")
def query_info(job: dict) -> JobInfo:
    # TODO: review this code
    cookies = load_cookies()
    api = LinkedInProcessing(cookies)

    job_info = api.get_job_info(job)
    try:
        job_info.summary = job_summary_openai(job_info.description).to_dataclass()
    except Exception as e:
        logging.exception(f"Error while processing {job_info}")

    return job_info.to_dict()


@app.activity_trigger(input_name="job")
@app.cosmos_db_output(
    arg_name="cosmos",
    database_name="linkedinjobs",
    container_name="jobs",
    connection="CosmosConnection",
)
def persist_job_info(job, cosmos: func.Out[func.Document]):
    data = job.to_dict()
    data["id"] = data["job_posting_id"]
    cosmos.set(func.Document.from_dict(data))
    return ""


from function import job_search_entity, job_process_entity

app.register_functions(job_search_entity.app)
app.register_functions(job_process_entity.app)

# job_search_entity.register_entity(app)

# @app.entity_trigger(context_name="context", entity_name="Counter")
# def entity_function(context: df.DurableEntityContext):
#     current_value = context.get_state(lambda: 0)
#     operation = context.operation_name
#     if operation == "add":
#         amount = context.get_input()
#         current_value += amount
#     elif operation == "reset":
#         current_value = 0
#     elif operation == "get":
#         context.set_result(current_value)
#     context.set_state(current_value)


# @app.route(route="EntityClient")
# @app.durable_client_input(client_name="starter")
# async def EntityTrigger(req: func.HttpRequest, starter: df.DurableOrchestrationClient) -> func.HttpResponse:
#     logging.info('Python HTTP trigger function processed a request.')
#     logging.info(starter)
#     entityId = df.EntityId("Counter", "myCounter")
#     logging.info(await starter.signal_entity(entityId, "add", 1))
#     logging.warn((await starter.get_status(entityId)).to_json())
#     logging.warn((await starter.read_entity_state(entityId)).entity_state)

#     return func.HttpResponse("")
