import sys
import requests
import json
import yaml
import re
import logging
from pathlib import Path
from os.path import isdir, dirname, join
from os import environ
from pprint import pformat
import pandas as pd

from hubmap_commons.exceptions import HTTPException
from werkzeug.exceptions import HTTPException as WerkzeugException

from source_is_human import source_is_human

from test_utils import print_rslt

logging.basicConfig(encoding="utf-8", level=logging.INFO)
LOGGER = logging.getLogger(__name__)

AUTH_TOK = environ.get("AUTH_TOK")
APP_CTX = environ.get("APP_CTX")

def get_urls():
    """
    Returns assaytype_url, entity_url as a tuple
    """
    if APP_CTX == "HUBMAP":
        #assaytype_url = 'https://ingest-api.test.hubmapconsortium.org/'
        #assaytype_url = 'https://ingest.api.hubmapconsortium.org/'
        assaytype_url = 'https://ingest-api.dev.hubmapconsortium.org/'
        entity_url = 'https://entity.api.hubmapconsortium.org/'
        return assaytype_url, entity_url
    elif APP_CTX == "SENNET":
        assaytype_url = 'https://ingest.api.sennetconsortium.org/'
        entity_url = 'https://entity.api.sennetconsortium.org/'
        return assaytype_url, entity_url
    else:
        if APP_CTX:
            raise RuntimeError(f"Unknown APP_CTX {APP_CTX}")
        else:
            raise RuntimeError("Environment does not contain APP_CTX")


def build_cached_json_fname(uuid, app_ctx,
                            dir="captured_entity_json",
                            prefix="entity"):
    """
    Return a full path to the expected location of the cached file, which has a
    basename of the form "entity_{uuid}_{app_ctx}.json"
    """
    fname = str(Path(__file__).parent / dir / f"{prefix}_{uuid}_{app_ctx}.json")
    return fname


def save_entity_json(uuid, app_ctx, json_dict):
    """Save a copy for future use in unit tests"""
    fname = build_cached_json_fname(uuid, app_ctx)
    LOGGER.info(f"Saving JSON to {fname}")
    with open(fname, "w") as ofile:
        json.dump(json_dict, ofile)
        ofile.write("\n")


def save_metadata_json(uuid, app_ctx, json_dict):
    """Save a copy for future use in unit tests"""
    fname = build_cached_json_fname(uuid, app_ctx,
                                    dir="captured_metadata_json",
                                    prefix="metadata")
    LOGGER.info(f"Saving metadata JSON to {fname}")
    with open(fname, "w") as ofile:
        json.dump(json_dict, ofile)
        ofile.write("\n")


def get_entity_json(ds_uuid: str) -> dict:
    """
    Given a uuid and the (implicit) request, return the
    entity.  This works for sources and samples as well as
    for datasets.
    """
    assert AUTH_TOK, "AUTH_TOK was not found in the environment"
    entity_url = get_urls()[1]
    response = requests.get(entity_url + 'entities/' + ds_uuid,
                            headers={"Authorization":f"Bearer {AUTH_TOK}"}
                            )
    response.raise_for_status()
    
    return response.json()


def get_metadata_json(ds_uuid:str) -> dict:
    """
    Given a uuid and the (implicit) request, return the
    metadata passed to the rule chain.
    """
    assert AUTH_TOK, "AUTH_TOK was not found in the environment"
    assaytype_url = get_urls()[0]
    rply = requests.get(
        assaytype_url + 'assaytype' + '/metadata/' + ds_uuid,
        headers={
            'Authorization': 'Bearer ' + AUTH_TOK,
            'content-type': 'application/json'
        }
    )
    rply.raise_for_status()
    
    return rply.json()


def get_rulechain_json(ds_uuid:str) -> dict:
    """
    Given a uuid and the (implicit) request, return the
    the output of the rule chain implementation on the endpoint.
    """
    assert AUTH_TOK, "AUTH_TOK was not found in the environment"
    assaytype_url = get_urls()[0]
    rply = requests.get(
        assaytype_url + 'assaytype/' + ds_uuid,
        headers={
            'Authorization': 'Bearer ' + AUTH_TOK,
            'content-type': 'application/json'
        }
    )
    rply.raise_for_status()
    
    return rply.json()


def main() -> None:
    if sys.argv[1] == "--help":
        print(
            f"""
            Usage: env AUTH_TOK='tokenstr' APP_CTK='SENNETorHUBMAP' {sys.argv[0]} uuid [uuid [uuid ...]]
            """
        )
    else:
        for uuid in sys.argv[1:]:
            try:
                entity_json = get_entity_json(uuid)
                save_entity_json(uuid, APP_CTX, entity_json)
                is_human = source_is_human([uuid], get_entity_json)
                LOGGER.info(f"{APP_CTX} {uuid} produces source_is_human {is_human}")
                payload = get_metadata_json(uuid)
                payload["source_is_human"] = is_human
                save_metadata_json(uuid, APP_CTX, payload)
                current_rule_output = get_rulechain_json(uuid)
                print_rslt("in-line uuid", uuid,
                           payload,
                           current_rule_output,
                           show_payload=True)
            except requests.exceptions.HTTPError as excp:
                LOGGER.error(f"ERROR: {excp}")
    LOGGER.info('done')

if __name__ == '__main__':
    main()
