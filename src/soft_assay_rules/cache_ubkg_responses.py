import logging
import sys
from os import environ
from pprint import pformat

import requests
from cache_responses import get_ubkg_json, save_ubkg_json

logging.basicConfig(encoding="utf-8", level=logging.INFO)
LOGGER = logging.getLogger(__name__)

APP_CTX = environ.get("APP_CTX")


def main() -> None:
    if sys.argv[1] == "--help":
        print(
            f"""
            Usage: env APP_CTX='SENNETorHUBMAP' {sys.argv[0]} uuid [uuid [uuid ...]]
            """
        )
    else:
        for ubkg_code in sys.argv[1:]:
            try:
                ubkg_json = get_ubkg_json(ubkg_code)
                LOGGER.info(f"{ubkg_code} ->\n{pformat(ubkg_json)}")
                save_ubkg_json(ubkg_code, APP_CTX, ubkg_json)
            except requests.exceptions.HTTPError as excp:
                LOGGER.error(f"ERROR: {excp}")
    LOGGER.info("done")


if __name__ == "__main__":
    main()
