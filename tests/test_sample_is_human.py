from pathlib import Path
import re
import json

import pandas as pd
import pytest
from pprint import pprint

from local_rule_tester import wrapped_lookup_json
from source_is_human import source_is_human


@pytest.mark.parametrize(('uuid', 'expected_value'), (
    ("c019a1cd35aab4d2b4a6ff221e92aaab", True),
    ("SNT658.QHTS.972", True),
    ("SNT594.FZCM.747", False)
))
def test_sample_is_human(uuid, expected_value, tmp_path):
    val = source_is_human([uuid], wrapped_lookup_json)
    assert val == expected_value
