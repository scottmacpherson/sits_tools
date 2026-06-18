"""Turn a Uniface List of JSON objects into a valid JSON list

One use case is for dealing with the output of a `SELECT JSON_OBJECT()…` query
via SWB. Set the output to Uniface List, save the result, and shove it through
this script.
"""

import argparse
import json
import pathlib
import sys

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("input_file", type=pathlib.Path)
    args = parser.parse_args()

    with open(args.input_file, "r") as f:
        raw_input = f.read()
    fixed_input = "[" + raw_input.replace("\x1b", ",") + "]"
    json_object = json.loads(fixed_input)

    json.dump(json_object, sys.stdout, indent=4)
