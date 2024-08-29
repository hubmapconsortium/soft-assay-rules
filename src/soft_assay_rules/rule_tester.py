import sys
import requests
import json
import yaml
import re
import logging
from os.path import isdir, dirname, join
from os import environ
from pprint import pformat
import pandas as pd

from hubmap_commons.exceptions import HTTPException
from werkzeug.exceptions import HTTPException as WerkzeugException

from source_is_human import source_is_human
from local_rule_tester import print_rslt

AUTH_TOK = environ['AUTH_TOK']
APP_CTX = environ['APP_CTX']
from cache_responses import (
    build_cached_json_fname,
    get_entity_json,
    get_metadata_json,
    ASSAYTYPE_URL
)

logging.basicConfig(encoding="utf-8", level=logging.INFO)
LOGGER = logging.getLogger(__name__)


def main() -> None:
    for argfile in sys.argv[1:]:
        if argfile.endswith('~'):
            LOGGER.info(f"Skipping {argfile}")
            continue  # probably an editor backup file
        if isdir(argfile):
            LOGGER.info(f"Skipping directory {argfile}")
            continue
        LOGGER.info(f"Reading {argfile}")
        if argfile.endswith('.tsv'):
            arg_df = pd.read_csv(argfile, sep='\t')
            if len(arg_df.columns) == 1 and 'uuid' in arg_df.columns:
                for idx, row in arg_df.iterrows():
                    try:
                        uuid = row['uuid']
                        is_human = source_is_human([uuid], get_entity_json)
                        LOGGER.info(f"source_is_human {[uuid]} returns {is_human}")
                        payload = get_metadata_json(uuid)
                        payload["source_is_human"] = is_human
                        rply = requests.get(
                            ASSAYTYPE_URL + 'assaytype' + '/' + uuid,
                            headers={
                                'Authorization': 'Bearer ' + AUTH_TOK,
                                'content-type': 'application/json'
                            }
                        )
                        rply.raise_for_status()
                        rslt = rply.json()
                        print_rslt(argfile, row['uuid'], payload, rslt, show_payload=True)
                    except requests.exceptions.HTTPError as excp:
                        LOGGER.error(f"ERROR: {excp}")
            else:
                for idx, row in arg_df.iterrows():
                    try:
                        payload = {col: row[col] for col in arg_df.columns}
                        if "parent_sample_id" in payload:
                            # This sample is new enough to have a column of parent
                            # samples, so we can check source type
                            parent_sample_ids = payload["parent_sample_id"].split(",")
                            parent_sample_ids = [elt.strip() for elt in parent_sample_ids]
                            is_human = source_is_human(parent_sample_ids, get_entity_json)
                            LOGGER.info(f"source_is_human {parent_sample_ids} returns {is_human}")
                        else:
                            is_human = True  # legacy data is all human
                        payload["source_is_human"] = is_human
                        rply = requests.post(
                            ASSAYTYPE_URL + 'assaytype',
                            data=json.dumps(payload),
                            headers={
                                'Authorization': 'Bearer ' + AUTH_TOK,
                                'content-type': 'application/json'
                            }
                        )
                        rply.raise_for_status()
                        rslt = rply.json()
                        print_rslt(argfile, idx, payload, rslt)
                    except requests.exceptions.HTTPError as excp:
                        LOGGER.error(f"ERROR: {excp}")
        elif argfile.endswith('.json'):
            try:
                with open(argfile) as jsonfile:
                    payload = json.load(jsonfile)
                assert "source_is_human" in payload, ("cached payload {argfile} lacks"
                                                      f" source_is_human")
                rply = requests.post(
                    ASSAYTYPE_URL + 'assaytype',
                    data=json.dumps(payload),
                    headers={
                        'Authorization': 'Bearer ' + AUTH_TOK,
                        'content-type': 'application/json'
                    }
                )
                rply.raise_for_status()
                rslt = rply.json()
                print_rslt(argfile, None, payload, rslt)
            except requests.exceptions.HTTPError as excp:
                LOGGER.error(f"ERROR: {excp}")
        else:
            raise RuntimeError(f"Arg file {argfile} is of an"
                               " unrecognized type")
    LOGGER.info('done')

if __name__ == '__main__':
    main()
