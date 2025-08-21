import json
from pprint import pprint


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
