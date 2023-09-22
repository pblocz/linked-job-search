from io import TextIOWrapper
from pathlib import Path
import json
from dataclasses import dataclass
import glob
from typing import Any, Generator


@dataclass
class StorageLayer:
    data_path: str = "data"

    def persist_on_storage(self, path, file_name, json_dict):
        path = Path(self.data_path) / path / file_name

        path.parent.mkdir(exist_ok=True, parents=True)

        if isinstance(json_dict, dict):
            dump_data = json.dumps(json_dict)
        else:
            dump_data = json_dict.to_json()

        with path.open("w") as f:
            f.write(dump_data)
        

    def load_from_storage(self, path_glob, mapping) -> Generator[TextIOWrapper, Any, None]:
        for file_path in glob.glob(str(Path("data") / path_glob)):
            with open(file_path, "r") as f:
                yield mapping(f.read())