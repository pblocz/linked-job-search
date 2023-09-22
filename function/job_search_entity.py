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
