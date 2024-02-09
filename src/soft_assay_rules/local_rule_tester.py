"""
This version of the rule tester runs locally, without reference to ingest-api or
entity-api .  This allows only a subset of functionality since it cannot support
uuid lookup, but it provides support for CI tests.
"""

import sys
import requests
import json
import yaml
import re
from pathlib import Path
from os.path import isdir
from pprint import pprint
import pandas as pd

from rule_chain import (
    RuleLoader,
    RuleChain,
    NoMatchException,
    RuleSyntaxException,
    RuleLogicException,
)

from rule_generator import CHAIN_OUTPUT_PATH as CHAIN_INPUT_PATH

rule_chain = None


def initialize_rule_chain():
    global rule_chain
    localized_chain_input_path = (Path(__file__).resolve().parent / CHAIN_INPUT_PATH).resolve()
    with open(localized_chain_input_path) as chain_file:
        rule_chain = RuleLoader(chain_file).load()


def calculate_assay_info(metadata: dict) -> dict:
    # TODO: this function should really get imported from ingest-api
    if not rule_chain:
        initialize_rule_chain()
    for key, value in metadata.items():
        if type(value) is str:
            if value.isdigit():
                metadata[key] = int(value)
    try:
        rslt = rule_chain.apply(metadata)
        # TODO: check that rslt has the expected parts
        return rslt
    except NoMatchException:
        return {}


def print_rslt(argfile, idx, payload, rslt, show_payload=False):
    """
    This just summarizes the results of a test case to stdout
    """
    if show_payload:
        print(f"{argfile} {idx if idx else ''} -> json metadata: {json.dumps(payload)} ->")
        pprint(rslt)
        if not rslt:
            print("NOT MAPPED!")
    else:
        print(f"{argfile} {idx if idx else ''} ->")
        pprint(rslt)
        if not rslt:
            print("NOT MAPPED!")
            print("Payload follows")
            pprint(payload)


def main() -> None:
    for argfile in sys.argv[1:]:
        if argfile.endswith('~'):
            print(f"Skipping {argfile}")
            continue  # probably an editor backup file
        if isdir(argfile):
            print(f"Skipping directory {argfile}")
            continue
        print(f"Reading {argfile}")
        arg_df = None
        if argfile.endswith('.tsv'):
            arg_df = pd.read_csv(argfile, sep='\t')
            if len(arg_df.columns) == 1 and 'uuid' in arg_df.columns:
                print(f"Skipping uuids in {argfile}; not supported in local mode")
            else:
                #print(arg_df)
                for idx, row in arg_df.iterrows():
                    payload = {col: row[col] for col in arg_df.columns}
                    rslt = calculate_assay_info(payload)
                    print_rslt(argfile, idx, payload, rslt)
        elif argfile.endswith('.json'):
            with open(argfile) as jsonfile:
                payload = json.load(jsonfile)
                rslt = calculate_assay_info(payload)
                print_rslt(argfile, 0, payload, rslt)
        else:
            raise RuntimeError(f"Arg file {argfile} is of an"
                               " unrecognized type")
    print('done')

if __name__ == '__main__':
    main()
