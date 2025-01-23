from pathlib import Path
import re
import json

import pandas as pd
import pytest
from pprint import pprint

from local_rule_tester import (
    calculate_assay_info,
    wrapped_lookup_entity_json,
    wrapped_lookup_ubkg_json
)
from source_is_human import source_is_human

@pytest.fixture
def test_sample_path():
    return (Path(__file__).resolve().parent.parent
            / 'src'
            / 'soft_assay_rules'
            / 'test_examples'
            )


def lists_to_sets(dct):
    """
    Convert the values in the input dict which are lists or tuples to sets,
    so that comparisons will not be order-dependent.
    """
    return {
        key: set(val) if isinstance(val, (list, tuple)) else val
        for key, val in dct.items()
    }


@pytest.mark.parametrize(('test_data_fname', 'expected'), (

    ("salmon_json_c019a1cd35aab4d2b4a6ff221e92aaab.json",
     {"assaytype": "salmon_sn_rnaseq_10x",
      "contains-pii": False,
      "dataset-type": "RNAseq",
      "description": "snRNAseq [Salmon]",
      "primary": False,
      "vitessce-hints": ("is_sc", "rna", "json_based"),
      'ubkg_code': 'C202000',
      'pipeline-shorthand': 'Salmon'}),

    ("salmon_anndata_e65175561b4b17da5352e3837aa0e497.json",
     {'assaytype': 'salmon_sn_rnaseq_10x',
      'contains-pii': False,
      'description': 'snRNAseq [Salmon]',
      'primary': False,
      'vitessce-hints': ('is_sc', 'rna'),
      'ubkg_code': 'C200630',
      'pipeline-shorthand': 'Salmon'}),

    ("codex_cytokit_89e4944336dd47d32a50fe8aac049db1.json",
     {'assaytype': 'codex_cytokit',
      'contains-pii': False,
      'description': 'CODEX [Cytokit + SPRM]',
      'primary': False,
      'vitessce-hints': ('sprm', 'anndata', 'is_image', 'is_tiled'),
      'ubkg_code': 'C200100',
      'pipeline-shorthand': 'Cytokit + SPRM'}),

    ("codex_cytokit_json_b69d1e2ad1bf1455eee991fce301b191.json",
     {'assaytype': 'codex_cytokit_v1',
      'contains-pii': False,
      'description': 'CODEX [Cytokit + SPRM]',
      'primary': False,
      'vitessce-hints': ('codex', 'is_image', 'is_tiled', 'json_based'),
      'ubkg_code': 'C200090',
      'pipeline-shorthand': 'Cytokit + SPRM'}),
    
    ("codex_cytokit_anndata_43213991a54ce196d406707ffe2e86bd.json",
     {'assaytype': 'codex_cytokit_v1',
      'contains-pii': False,
      'description': 'CODEX [Cytokit + SPRM]',
      'primary': False,
      'vitessce-hints': ('codex', 'is_image', 'is_tiled', 'anndata'),
      'ubkg_code': 'C200080',
      'pipeline-shorthand': 'Cytokit + SPRM'},
     ),

    ("salmon_json_e8d642084fc5ec8b5d348ebab96a4b22.json",
     {'assaytype': 'salmon_rnaseq_10x',
      'contains-pii': False,
      'dataset-type': 'RNAseq',
      'description': 'scRNAseq (10x Genomics) [Salmon]',
      'primary': False,
      'vitessce-hints': ('is_sc', 'rna', 'json_based'),
      'ubkg_code': 'C202010',
      'pipeline-shorthand': 'Salmon'}),

    ("salmon_anndata_6efe308f2e7360127e47865edf075424.json",
     {'assaytype': 'salmon_rnaseq_10x',
      'contains-pii': False,
      'dataset-type': 'RNAseq',
      'description': 'scRNAseq (10x Genomics) [Salmon]',
      'primary': False,
      'vitessce-hints': ('is_sc', 'rna'),
      'ubkg_code': 'C200500',
      'pipeline-shorthand': 'Salmon'}),

    ("metadata_SNT594.FZCM.747_SENNET.json",
     {'assaytype': 'scRNAseq-10xGenomics-v3',
      'contains-pii': False,
      'dataset-type': 'RNAseq',
      'description': 'scRNAseq (10x Genomics v3)',
      'dir-schema': 'rnaseq-v2',
      'primary': True,
      'ubkg_code': 'C200850',
      'vitessce-hints': ()}),

    ("metadata_HBM263.FTWN.879_visium_rnaseq_hubmap.tsv",
     {'assaytype': 'rnaseq-visium-no-probes',
      'contains-pii': True,
      'dataset-type': 'RNAseq',
      'description': 'Capture bead RNAseq (10x Genomics v3)',
      'dir-schema': 'rnaseq-v2',
      'primary': True,
      'ubkg_code': 'C200810',
      'vitessce-hints': ()}),

    ("metadata_SNT588.HFTQ.737_visium_sennet.tsv",
     {'assaytype': 'visium-no-probes',
      'contains-pii': True,
      'dataset-type': 'Visium (no probes)',
      'description': 'Visium (no probes)',
      'dir-schema': 'visium-no-probes-v3',
      'is-multi-assay': True,
      'must-contain': ('Histology', 'RNAseq'),
      'primary': True,
      'ubkg_code': 'C200740',
      'vitessce-hints': ()}),

    ("metadata_SNT588.HFTQ.737_visium_hande_sennet.tsv",
     {'assaytype': 'h-and-e',
      'contains-pii': False,
      'dataset-type': 'Histology',
      'description': 'H&E Stained Microscopy',
      'dir-schema': 'histology-v2',
      'primary': True,
      'ubkg_code': 'C200940',
      'vitessce-hints': ()}),

    ("metadata_SNT588.HFTQ.737_visium_scrnaseq_sennet.tsv",
     {'assaytype': 'rnaseq-visium-no-probes',
      'contains-pii': True,
      'dataset-type': 'RNAseq',
      'description': 'Capture bead RNAseq (10x Genomics v3)',
      'dir-schema': 'rnaseq-v2',
      'primary': True,
      'ubkg_code': 'C200810',
      'vitessce-hints': ()}),

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
            if "parent_sample_id" in payload:
                # This sample is new enough to have a column of parent
                # samples, so we can check source type
                parent_sample_ids = payload["parent_sample_id"].split(",")
                parent_sample_ids = [elt.strip() for elt in parent_sample_ids]
                is_human = source_is_human(parent_sample_ids,
                                           wrapped_lookup_entity_json)
            else:
                is_human = True  # legacy data is all human
            rslt = calculate_assay_info(payload, is_human,
                                        wrapped_lookup_ubkg_json)
            assert rslt, f"{test_data_fname} record {idx} failed"
    elif str(md_path).endswith('.json'):
        with open(md_path) as jsonfile:
            payload = json.load(jsonfile)
            print(json.dumps(payload))
            if "parent_sample_id" in payload:
                # This sample is new enough to have a value for parent
                # samples, so we can check source type
                parent_sample_ids = payload["parent_sample_id"].split(",")
                parent_sample_ids = [elt.strip() for elt in parent_sample_ids]
                is_human = source_is_human(parent_sample_ids,
                                           wrapped_lookup_entity_json)
            else:
                is_human = True  # legacy data is all human
            rslt = calculate_assay_info(payload, is_human,
                                        wrapped_lookup_ubkg_json)
            assert rslt, f"{test_data_fname} record failed"
    else:
        assert False, f"Metadata path {md_path} is not .tsv or .json"
    assert lists_to_sets(rslt) == lists_to_sets(expected)
