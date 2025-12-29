import base64
import json
import sys

import adac
import mobilede

ARGUMENTS_LEN_REQUIRED = 3

if __name__ == "__main__":
    if len(sys.argv) != ARGUMENTS_LEN_REQUIRED:
        sys.exit(1)

    data = base64.b64decode(sys.argv[2]).decode("utf-8")

    output = None

    if sys.argv[1] == "mobilede":
        output = mobilede.get_cars_from_url(data)
    elif sys.argv[1] == "adac":
        output = adac.get_info_from_search_strings(data)
    else:
        sys.exit(1)

    print(json.dumps(output, indent=2, ensure_ascii=False))  # noqa: T201
