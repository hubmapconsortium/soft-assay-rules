from pathlib import Path
import re
import json

import pandas as pd
import pytest
from pprint import pprint

from local_rule_tester import calculate_assay_info

@pytest.fixture
def test_sample_path():
    return (Path(__file__).resolve().parent.parent
            / 'src'
            / 'soft_assay_rules'
            / 'test_examples'
            )
    

@pytest.mark.parametrize(('test_data_fname', 'expected'), (

    ("salmon_json_c019a1cd35aab4d2b4a6ff221e92aaab.json",
     {"assaytype": "salmon_sn_rnaseq_10x",
      "contains-pii": False,
      "description": "snRNA-seq [Salmon]",
      "primary": False,
      "vitessce-hints": ("is_sc", "rna", "json_based")}),

    ("salmon_anndata_e65175561b4b17da5352e3837aa0e497.json",
     {'assaytype': 'salmon_sn_rnaseq_10x',
      'contains-pii': False,
      'description': 'snRNA-seq [Salmon]',
      'primary': False,
      'vitessce-hints': ('is_sc', 'rna')}),

    ("codex_cytokit_89e4944336dd47d32a50fe8aac049db1.json",
     {'assaytype': 'codex_cytokit',
      'contains-pii': False,
      'description': 'CODEX [Cytokit + SPRM]',
      'primary': False,
      'vitessce-hints': ('sprm', 'anndata', 'is_image', 'is_tiled')}),

    ("codex_cytokit_json_b69d1e2ad1bf1455eee991fce301b191.json",
     {'assaytype': 'codex_cytokit_v1',
      'contains-pii': False,
      'description': 'CODEX [Cytokit + SPRM]',
      'primary': False,
      'vitessce-hints': ('codex', 'is_image', 'is_tiled', 'json_based')}),
    
    ("codex_cytokit_anndata_43213991a54ce196d406707ffe2e86bd.json",
     {'assaytype': 'codex_cytokit_v1',
      'contains-pii': False,
      'description': 'CODEX [Cytokit + SPRM]',
      'primary': False,
      'vitessce-hints': ('codex', 'is_image', 'is_tiled', 'anndata')}),

    ("salmon_json_e8d642084fc5ec8b5d348ebab96a4b22.json",
     {'assaytype': 'salmon_rnaseq_10x',
      'contains-pii': False,
      'description': 'scRNA-seq (10x Genomics) [Salmon]',
      'primary': False,
      'vitessce-hints': ('is_sc', 'rna', 'json_based')}),

    ("salmon_anndata_6efe308f2e7360127e47865edf075424.json",
     {'assaytype': 'salmon_rnaseq_10x',
      'contains-pii': False,
      'description': 'scRNA-seq (10x Genomics) [Salmon]',
      'primary': False,
      'vitessce-hints': ('is_sc', 'rna')})
))
def test_rule_match_case(test_sample_path, test_data_fname, expected, tmp_path):
    md_path = test_sample_path / test_data_fname
    print(f"MD_PATH: {md_path}")
    assert md_path.is_file()
    if str(md_path).endswith('.tsv'):
        arg_df = pd.read_csv(str(md_path), sep='\t')
        print(arg_df)
        for idx, row in arg_df.iterrows():
            payload = {col: row[col] for col in arg_df.columns}
            rslt = calculate_assay_info(payload)
            assert rslt, f"{test_data_fname} record {idx} failed"
    elif str(md_path).endswith('.json'):
        with open(md_path) as jsonfile:
            payload = json.load(jsonfile)
            print(json.dumps(payload))
            rslt = calculate_assay_info(payload)
            assert rslt, f"{test_data_fname} record failed"
    else:
        assert False, f"Metadata path {md_path} is not .tsv or .json"
    assert rslt == expected
