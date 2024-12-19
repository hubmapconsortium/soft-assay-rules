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
import logging
from pathlib import Path
from pprint import pprint, pformat
import pandas as pd

from source_is_human import source_is_human

from cache_responses import build_cached_json_fname

from test_utils import print_rslt

from rule_chain import (
    RuleLoader,
    RuleChain,
    NoMatchException,
    RuleSyntaxException,
    RuleLogicException,
)

logging.basicConfig(encoding="utf-8", level=logging.INFO)
LOGGER = logging.getLogger(__name__)

CHAIN_INPUT_PATH = Path(__file__).parent / "testing_rule_chain.json"

rule_chain = None


def initialize_rule_chain():
    global rule_chain
    localized_chain_input_path = (Path(__file__).resolve().parent / CHAIN_INPUT_PATH).resolve()
    with open(localized_chain_input_path) as chain_file:
        rule_chain = RuleLoader(chain_file).load()


def lookup_entity_json(uuid):
    """
    Check the directory of cached entity json files for the given example, looking for
    filenames of the form "entity_{uuid}_SENNET.json" or ..."_HUBMAP.json".  Pick the
    first of those found, and infer the uuid's app_ctx from the corresponding string.
    Return a tuple containing that app_ctx as a string and the JSON dict loaded from
    the file.  If no such file is found, ValueError is raised.
    """
    for app_ctx in ["SENNET", "HUBMAP"]:
        fname = build_cached_json_fname(uuid, app_ctx)
        if Path(fname).exists():
            with open(fname) as infile:
                json_dict = json.load(infile)
                LOGGER.debug(f"JSON provided: {json_dict.keys()}")
            return app_ctx, json_dict
    raise ValueError(f"No cached JSON for {uuid}")


def wrapped_lookup_entity_json(uuid):
    """Like lookup_entity_json but drop the app_ctx"""
    return lookup_entity_json(uuid)[1]


def lookup_metadata_json(uuid):
    """
    Check the directory of cached metadata json files for the given example, looking for
    filenames of the form "metadata_{uuid}_SENNET.json" or ..."_HUBMAP.json".  Pick the
    first of those found, and infer the uuid's app_ctx from the corresponding string.
    Return a tuple containing that app_ctx as a string and the JSON dict loaded from
    the file.  If no such file is found, ValueError is raised.
    """
    for app_ctx in ["SENNET", "HUBMAP"]:
        fname = build_cached_json_fname(uuid, app_ctx,
                                        dir="captured_metadata_json",
                                        prefix="metadata")
        if Path(fname).exists():
            with open(fname) as infile:
                json_dict = json.load(infile)
            return app_ctx, json_dict
    raise ValueError(f"No cached metadata JSON for {uuid}")


def wrapped_lookup_metadata_json(uuid):
    """Like lookup_metadata_json but drop the app_ctx"""
    return lookup_metadata_json(uuid)[1]


def lookup_rulechain_json(uuid):
    """
    Check the directory of cached rulechain json files for the given example, looking for
    filenames of the form "rulechain_{uuid}_SENNET.json" or ..."_HUBMAP.json".  Pick the
    first of those found, and infer the uuid's app_ctx from the corresponding string.
    Return a tuple containing that app_ctx as a string and the JSON dict loaded from
    the file.  If no such file is found, ValueError is raised.
    """
    for app_ctx in ["SENNET", "HUBMAP"]:
        fname = build_cached_json_fname(uuid, app_ctx,
                                        dir="captured_rulechain_json",
                                        prefix="rulechain")
        if Path(fname).exists():
            with open(fname) as infile:
                json_dict = json.load(infile)
            return app_ctx, json_dict
    raise ValueError(f"No cached rulechain JSON for {uuid}")


def wrapped_lookup_rulechain_json(uuid):
    """Like lookup_rulechain_json but drop the app_ctx"""
    return lookup_rulechain_json(uuid)[1]


def post_rule_transform(rule_output: dict,
                        source_is_human: bool) -> dict:
    rslt = rule_output.copy()
    if "contains-pii" in rslt:
        rslt["contains-pii"] = rslt["contains-pii"] and source_is_human
    return rslt


def calculate_assay_info(metadata: dict, source_is_human: bool) -> dict:
    # TODO: this function should really get imported from ingest-api
    if not rule_chain:
        initialize_rule_chain()
    for key, value in metadata.items():
        if type(value) is str:
            if value.isdigit():
                metadata[key] = int(value)
    try:
        rslt = post_rule_transform(rule_chain.apply(metadata),
                                   source_is_human)
        # TODO: check that rslt has the expected parts
        return rslt
    except NoMatchException:
        return {}


def smart_equality(val1, val2):
    """
    Provide a more robust equality test for json blob terms. Compare lists
    as sets, etc.
    """
    if isinstance(val1, (list, tuple)):
        if isinstance(val2, list):
            return set(val1) == set(val2)
        else:
            return False
    else:
        return val1 == val2


def main() -> None:
    for argfile in sys.argv[1:]:
        if argfile.endswith('~'):
            LOGGER.info(f"Skipping {argfile}")
            continue  # probably an editor backup file
        if Path(argfile).is_dir():
            LOGGER.info(f"Skipping directory {argfile}")
            continue
        LOGGER.info(f"Reading {argfile}")
        arg_df = None
        if argfile.endswith('.tsv'):
            arg_df = pd.read_csv(argfile, sep='\t')
            if len(arg_df.columns) == 1 and 'uuid' in arg_df.columns:
                for idx, row in arg_df.iterrows():
                    uuid = row["uuid"]
                    app_ctx, json_dict = lookup_entity_json(uuid)
                    LOGGER.info(f"app_ctx for {uuid} is {app_ctx}")
                    is_human = source_is_human([uuid], wrapped_lookup_entity_json)
                    LOGGER.info(f"source_is_human for [{uuid}] returns {is_human}")
                    payload = wrapped_lookup_metadata_json(uuid)
                    LOGGER.debug(f"PAYLOAD: \n" + pformat(payload))
                    rslt = calculate_assay_info(payload, is_human)
                    cached_rslt = wrapped_lookup_rulechain_json(uuid)
                    for elt in rslt:
                        val = rslt[elt]
                        cached_val = cached_rslt.get(elt)
                        if not smart_equality(val, cached_val):
                            LOGGER.warning(f"DISCORDANT for {uuid} {elt}:"
                                           f" {val} != {cached_val}")
                    print_rslt(argfile, idx, payload, rslt)
            else:
                for idx, row in arg_df.iterrows():
                    payload = {col: row[col] for col in arg_df.columns}
                    if "parent_sample_id" in payload:
                        # This sample is new enough to have a column of parent
                        # samples, so we can check source type
                        parent_sample_ids = payload["parent_sample_id"].split(",")
                        parent_sample_ids = [elt.strip() for elt in parent_sample_ids]
                        is_human = source_is_human(parent_sample_ids, wrapped_lookup_entity_json)
                        LOGGER.info(f"source_is_human {parent_sample_ids} returns {is_human}")
                    else:
                        is_human = True  # legacy data is all human
                    rslt = calculate_assay_info(payload, is_human)
                    print_rslt(argfile, idx, payload, rslt)
        elif argfile.endswith('.json'):
            with open(argfile) as jsonfile:
                payload = json.load(jsonfile)
                # This reloaded payload was captured from a valid assayclassifier
                # version, so the payload should be complete- no added elements
                # needed.  But we have no way to tell if the source was human,
                # so assume that it is human.
                LOGGER.debug(f"RELOADED PAYLOAD: \n" + pformat(payload))
                rslt = calculate_assay_info(payload, True)
                print_rslt(argfile, 0, payload, rslt)
        else:
            raise RuntimeError(f"Arg file {argfile} is of an"
                               " unrecognized type")
    LOGGER.info('done')

if __name__ == '__main__':
    main()
