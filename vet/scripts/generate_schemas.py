import json
import os

import msgspec

from vet.models.config import TopLevelConfig

if __name__ == "__main__":
    config_schema_dict = msgspec.json.schema(TopLevelConfig)
    # export jsonschema
    with open(
        os.path.join(
            "schemas",
            "config_schema.json",
        ),
        "w",
    ) as f:
        f.write(json.dumps(config_schema_dict, indent=2))
