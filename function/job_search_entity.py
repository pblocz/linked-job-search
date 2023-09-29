from dataclasses import dataclass, field
import json
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
        return self

    def set(self, date):
        self.value = date
        return self
    
    def get(self):
        return self.value

    def get_float_value(self):
        return json.loads(self.to_json())["value"]
    
    @staticmethod
    def from_float_value(value):
        return JobSearchWatermark.from_json(json.dumps({"value": value}))

@app.entity_trigger(context_name="context", entity_name="JobSearchWatermark")
def job_search_watermark_entity_function(context: df.DurableEntityContext):
    current_value = context.get_state(lambda: JobSearchWatermark().get_float_value())
    # logging.info(f"running entity {context.entity_name}@{context.entity_key} with op={context.operation_name} cur={current_value} inp={context.get_inputt()}")
    logging.info(f"running entity {context.entity_name}@{context.entity_key} with op={context.operation_name} cur={current_value}")

    match context.operation_name:
        case "update":
            # current_value = datetime.now()
            current_value = JobSearchWatermark().update().get_float_value()
        case "set":
            # current_value = context.get_input()
            current_value = context.get_input()
        case "get":
            pass

    context.set_state(current_value)
    context.set_result(current_value)

@app.route(route="reset_entity")
@app.durable_client_input(client_name="client")
async def reset_job_search_watermark(req: func.HttpRequest, client: df.DurableOrchestrationClient) -> func.HttpResponse:

    current_time = JobSearchWatermark(datetime.now() - timedelta(hours=1))

    keywords = "Senior Data Scientist"
    entityId = df.EntityId("JobSearchWatermark", keywords)
    entity = await client.signal_entity(entityId, "set", current_time.get_float_value())

    keywords = "Senior Data Engineer"
    entityId = df.EntityId("JobSearchWatermark", keywords)
    entity = await client.signal_entity(entityId, "set", current_time.get_float_value())

    return func.HttpResponse("")

@app.route(route="update_entity")
@app.durable_client_input(client_name="client")
async def updae_job_search_watermark(req: func.HttpRequest, client: df.DurableOrchestrationClient) -> func.HttpResponse:

    keywords = "Senior Data Scientist"
    entityId = df.EntityId("JobSearchWatermark", keywords)
    entity = await client.signal_entity(entityId, "update")

    keywords = "Senior Data Engineer"
    entityId = df.EntityId("JobSearchWatermark", keywords)
    entity = await client.signal_entity(entityId, "update")

    return func.HttpResponse("")