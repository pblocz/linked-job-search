from dataclasses import dataclass, field
import azure.functions as func
import azure.durable_functions as df
import logging
from datetime import datetime, timedelta

from dataclasses_json import dataclass_json

app = df.Blueprint()

@app.entity_trigger(context_name="context", entity_name="JobProcessed")
def job_processed_entity_function(context: df.DurableEntityContext):
    current_value = context.get_state(lambda: False)

    match context.operation_name:
        case "set":
            current_value = True
        case "get":
            pass

    context.set_state(current_value)
    context.set_result(current_value)
