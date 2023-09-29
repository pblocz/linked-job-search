# Setup for Azure Functions for path and settins
# This is probably as fixtures in the future

import os
import sys
from pathlib import Path
import json


# Add root of function to path
root_dir_path = Path(__file__).resolve().parent.parent
root_dir = str(root_dir_path)
sys.path.append(root_dir)


# Add local settings to environment
with (root_dir_path / "local.settings.json").open() as f:
    local_settings = json.load(f)

for k, v in local_settings["Values"].items():
    os.environ[k] = v