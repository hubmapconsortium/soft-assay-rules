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

