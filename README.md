# soft-assay-rules

Rules for "soft" assay classification, and tools to generate and test them.

## About

Between the time a dataset is submitted by a data provider and the time it is accessed
by a potential user, many steps must occur.
* The provided dataset or upload must be validated as syntactially correct.
* The data must be "ingested", so that its type, location, and properties are known to the
larger system.
* The dataset must be processed to make its content useful. For example, image stitching or
RNA analysis may be required.  The steps required depend on the detailed structure of the
data.
* The data and the results of the analysis must be displayed to the user.  This again
depends on the detailed structure of the data and that of the derived data produced by any
analysis.

The *Soft Assay Classifier Rule Engine* is one mechanism by which these relationships are
managed.  A set of rules is applied to a detailed description of the original data format. Rules
that match the data are activated, yielding a summary of the properties of the data which can
be used by various downstream components to decide how to describe, display, or process the
data.  This repo contains the development history of the rule chain, plus tools to generate
and test the rule chain.  When a new version of the rule chain is ready it is exported to
another repo to actually be installed in the rule engine.

Once installed, the rule chain can be triggered in response to a POST request containing
a metadata.tsv record in JSON form, or in response to a GET request including a uuid or
HuBMAP/SenNet ID.  In the the former case the rule chain is passed only the given JSON
with an added pair with with key "sample_is_human" and a boolean value.  This POST
mechanism is used when validating and ingesting new external data.

When called with a GET request and uuid or ID, the entity JSON block for the given
entity is fetched and several values are produced from that metadata if possible,
including:
* the ingest metadata, if present
* the entity type, typically 'Dataset' or 'Publication'
* information from the dag provenance list, or an empty list if it is unavailable
* data_types information
* the entity creation action
* sample_is_human, as inferred from the entity provenance

These values are used to construct a JSON block which is passed to the rule chain.


## Running Unit Tests

Assuming the python environment specified in `requirements.txt` is in place, unit tests can be
run from the top level directory test.sh script:
```
bash ./test.sh
```

## Running Other Test Routines

The `src/soft_assay_rules` directory contains two test routines, `rule_tester.py` and `local_rule_tester.py` .
Both use the samples in the `test_examples` subdirectory.  local_rule_tester.py uses cached values previously
fetched from the appropriate services (see the section on cached REST endpoint responses below).
The first of these accesses an ingest-api URL to run tests against a remote running rule engine,
and thus requires a live token.  The token is provided through the environment variable AUTH_TOK .  Since
opertions in the context of SENNET differ slightly from those in the HUBMAP context, that context must
also be provided.  For example,
```
env AUTH_TOK=<some token> APP_CTX=<HUBMAP or SENNET> python rule_tester.py test_examples/*
```
tests the remote rule engine against all the samples in the `test_examples` directory.  If the SENNET
context is specified, examples taken from the HuBMAP side will fail, and vice versa.

`local_rule_tester.py` instantiates a local rule engine and installs the rules found in the
current `testing_rule_chain.json` file.  It can be used to test new rules.  Because it cannot query
entity-api when a uuid is specified, it must use cached results from the necessary queries.  (See
the section on cached REST endpoint responses below).  This test routine is invokes
as follows:
```
$ python ./local_rule_tester.py test_examples/*
```
## Cached REST Endpoint Responses

The utility routine `cache_responses.py` can be used to prefetch and save the entity-api metadata JSON
blocks associated with a given uuid or HuBMAP/SenNet ID.  It is called as follows:
```
env AUTH_TOK=<some token> APP_CTX=<HUBMAP or SENNET> python cache_responses.py uuid1 [uuid2 [uuid3...]]
```
This causes the entity-api JSON content for the uuid and the ingest-api/assayclassifier/metadata JSON
content to be fetched and stored locally.  (If the value of "sample_is_human" is not present in the
ingest-api/assayclassifier/metadata JSON fetched from the endpoint, it is inferred from the entity-api
data and added before the JSON is cached).  The JSON returned by the deployed version of the rule chain
is printed, for convenience in setting up new unit tests.  Thus a new unit test corresponding to a
specific uuid in a specific APP_CTX can be set up by:
* prefetching and saving the appropriate JSON using `cache_responses.py`
* creating a new test case using that uuid, or the ingest metadata for that uuid
* saving the expected JSON output of the rule chain as the desired test output
