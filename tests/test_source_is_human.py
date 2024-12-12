from pathlib import Path
import re
import json
import logging

import pandas as pd
import pytest
from pprint import pprint

from local_rule_tester import wrapped_lookup_json
from source_is_human import source_is_human

logging.basicConfig(encoding="utf-8", level=logging.INFO)
LOGGER = logging.getLogger(__name__)

@pytest.mark.parametrize(('uuid_list', 'expected_value'), (
    (["c019a1cd35aab4d2b4a6ff221e92aaab"], True),
    (["SNT658.QHTS.972"], True),
    (["SNT594.FZCM.747"], False),
    (["SNT658.QHTS.972", "SNT594.FZCM.747"], True),
    (["SNT594.FZCM.747", "SNT658.QHTS.972"], True),
    (["SYNTH1"], True),
))
def test_source_is_human(uuid_list, expected_value, tmp_path, caplog):
    with caplog.at_level(logging.DEBUG):
        val = source_is_human(uuid_list, wrapped_lookup_json)
        assert val == expected_value
