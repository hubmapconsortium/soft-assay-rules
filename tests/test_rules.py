from pathlib import Path
import re

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
    

@pytest.mark.parametrize(('test_data_fname'), (
    'validated-HuBMAP-Visium-RNAseq-metadata_1rec.tsv',
    'validated-HuBMAP-Visium-assay-metadata_1rec.tsv',
    'validated-HuBMAP-Visium-Histology-metadata_1rec.tsv',
    'codex_with_version_number.tsv',
    'dcwg_histology_metadata.tsv',
    'e45724a72ab0e7d7b283451836dd983e_codex_metadata.tsv',
    'validated-TEST-Histology-1rec-metadata.tsv',
    'validated-TEST-RNAseq-1rec-metadata_updated_20231031.tsv',
    'visium_sennet_v2_histology_1rec.tsv',
#    'visium_sennet_v2_rnaseq_1rec.tsv',
#    'visium_sennet_v2_visium_1rec.tsv',
    ))
def test_rule_case(test_sample_path, test_data_fname, tmp_path):
    md_path = test_sample_path / test_data_fname
    assert md_path.is_file()
    arg_df = None
    assert str(md_path).endswith('.tsv'), f"Arg file {md_path} is of an unrecognized type"
    arg_df = pd.read_csv(str(md_path), sep='\t')
    print(arg_df)
    for idx, row in arg_df.iterrows():
        payload = {col: row[col] for col in arg_df.columns}
        rslt = calculate_assay_info(payload)
        assert rslt, f"{test_data_fname} record {idx} failed"
