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

## Running Unit Tests

Assuming the python environment specified in `requirements.txt` is in place, unit tests can be
run from the top level directory test.sh script:
```
bash ./test.sh
```

## Running Other Test Routines

The `src/soft_assay_rules` directory contains two test routines, `rule_tester.py` and `local_rule_tester.py` .
Both use the samples in the `test_examples` subdirectory.
The first of these accesses a (hard-coded) ingest-api URL to run tests against a remote running rule engine,
and thus requires a live token.  The token is provided through the environment variable AUTH_TOK .  For example,
```
env AUTH_TOK=<some token> python rule_tester.py test_examples/*
```
tests the remote rule engine against all the samples in the `test_examples` directory.

In contrast,`local_rule_tester.py` instantiates a local rule engine and installs the rules found in the
current `testing_rule_chain.json` file.  It can be used to test new rules, but because it cannot actually
look up datasets via entity-api it must ignore test cases for which only a uuid is given.  It is invoked
as:
```
$ python ./local_rule_tester.py test_examples.*
```
