from dataclasses import dataclass, field
import azure.functions as func
import azure.durable_functions as df
import logging
from datetime import datetime, timedelta

from dataclasses_json import dataclass_json

app = df.Blueprint()


@dataclass_json
@dataclass
class JobSearchWatermark:
    value: datetime = field(default_factory=lambda: datetime.now() - timedelta(days=1))

    def update(self):
        self.value = datetime.now()

    def set(self, date):
        self.value = date
    
    def get(self):
        return self.value


@app.entity_trigger(context_name="context", entity_name="JobSearchWatermark")
def job_search_watermark_entity_function(context: df.DurableEntityContext):
    current_value = context.get_state(lambda: JobSearchWatermark())
    # logging.info(f"running entity {context.entity_name}@{context.entity_key} with op={context.operation_name} cur={current_value} inp={context.get_inputt()}")
    logging.info(f"running entity {context.entity_name}@{context.entity_key} with op={context.operation_name} cur={current_value}")

    match context.operation_name:
        case "update":
            # current_value = datetime.now()
            current_value.update()
        case "set":
            # current_value = context.get_input()
            current_value.set(context.get_input().value)
        case "get":
            pass

    context.set_state(current_value)
    context.set_result(current_value)

@app.route(route="reset_entity")
@app.durable_client_input(client_name="client")
async def reset_job_search_watermark(req: func.HttpRequest, client: df.DurableOrchestrationClient) -> func.HttpResponse:

    current_time = JobSearchWatermark(datetime.now() - timedelta(days=4))

    keywords = "Senior Data Scientist"
    entityId = df.EntityId("JobSearchWatermark", keywords)
    entity = await client.signal_entity(entityId, "set", current_time)

    keywords = "Senior Data Engineer"
    entityId = df.EntityId("JobSearchWatermark", keywords)
    entity = await client.signal_entity(entityId, "set", current_time)

    return func.HttpResponse("")

@app.route(route="update_entity")
@app.durable_client_input(client_name="client")
async def updae_job_search_watermark(req: func.HttpRequest, client: df.DurableOrchestrationClient) -> func.HttpResponse:

    current_time = JobSearchWatermark(datetime.now() - timedelta(days=4))

    keywords = "Senior Data Scientist"
    entityId = df.EntityId("JobSearchWatermark", keywords)
    entity = await client.signal_entity(entityId, "update")

    keywords = "Senior Data Engineer"
    entityId = df.EntityId("JobSearchWatermark", keywords)
    entity = await client.signal_entity(entityId, "update")

    return func.HttpResponse("")