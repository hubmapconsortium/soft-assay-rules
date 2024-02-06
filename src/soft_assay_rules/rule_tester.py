import sys
import requests
import json
import yaml
import re
from os.path import isdir
from os import environ
from pprint import pprint
import pandas as pd

from local_rule_tester import print_rslt

AUTH_TOK = environ['AUTH_TOK']

#TEST_BASE_URL = 'http://localhost:5000/'
TEST_BASE_URL = 'https://ingest-api.test.hubmapconsortium.org/'

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
                for idx, row in arg_df.iterrows():
                    try:
                        print(f"AUTH_TOK: {AUTH_TOK}")
                        rply = requests.get(
                            TEST_BASE_URL + 'assaytype' + '/metadata/' + row['uuid'],
                            headers={
                                'Authorization': 'Bearer ' + AUTH_TOK,
                                'content-type': 'application/json'
                            }
                        )
                        rply.raise_for_status()
                        payload = rply.json()
                        rply = requests.get(
                            TEST_BASE_URL + 'assaytype' + '/' + row['uuid'],
                            headers={
                                'Authorization': 'Bearer ' + AUTH_TOK,
                                'content-type': 'application/json'
                            }
                        )
                        rply.raise_for_status()
                        rslt = rply.json()
                        print_rslt(argfile, row['uuid'], payload, rslt, show_payload=True)
                    except requests.exceptions.HTTPError as excp:
                        print(f"ERROR: {excp}")
            else:
                for idx, row in arg_df.iterrows():
                    try:
                        payload = {col: row[col] for col in arg_df.columns}
                        rply = requests.post(
                            TEST_BASE_URL + 'assaytype',
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
                        print(f"ERROR: {excp}")
        elif argfile.endswith('.json'):
            try:
                with open(argfile) as jsonfile:
                    payload = json.load(jsonfile)
                rply = requests.post(
                    TEST_BASE_URL + 'assaytype',
                    data=json.dumps(payload),
                    headers={
                        'Authorization': 'Bearer ' + AUTH_TOK,
                        'content-type': 'application/json'
                    }
                )
                rply.raise_for_status()
                rslt = rply.json()
                print(f"{argfile} {idx} ->")
                pprint(rslt)
                if not rslt:
                    print("Payload follows")
                    pprint(payload)
    print('done')

if __name__ == '__main__':
    main()
