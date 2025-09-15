# PolarBayes quickstart for tidybayes users

If you have used tidybayes before, PolarBayes should feel familiar. The key functions are still named [`spread_draws`][polarbayes.spread.spread_draws] and [`gather_draws`][polarbayes.gather.gather_draws], and they still yield tidy data frames indexed by MCMC draw, with additional index columns for array-valued parameters. This quickstart walks you through the key differences between the two packages' APIs, and the reasons they arise.

## Key differences between tidybayes and PolarBayes

### No dots in column names

Reserved column names in tidybayes output begin with dots (`.`): `.chain`, `.iteration`, `.draw`, `.variable`, and `.value`. PolarBayes avoids dots in variable names because dots have a special role in Python syntax. Python is [object-oriented](https://en.wikipedia.org/wiki/Object-oriented_programming). In Python, as in many object-oriented programming languages, dots are used to access "attributes" and "methods" associated to particular objects.

NOTE: As you may know, R also has object-oriented features. The equivalent R operator to the python dot (`.`) is the dollar sign (`$`). You may have written `df$.draw` to retrieve a column named `.draw` from a data frame named `df`. So a polars column name like `.draw` is potentially a bad idea in the same way that a data frame column name like `$draw` could be a bad idea in R.

In PolarBayes, we instead reserve the bare column names `chain` and `draw` for indexing, consistent with ArviZ conventions for indexing MCMC output. If you try to extract variables with those name names from an [`arviz.InferenceData`][] object, PolarBayes will error and suggest renaming those variables prior to extraction.

### `draw` in PolarBayes corresponds to `.iteration` in tidybayes (_not_ `.draw`!)
In `tidybayes`, the `.draw` column contains the unique ID of an MCMC sample across all chains (in relational database terms, it is a [single column "primary key"](https://en.wikipedia.org/wiki/Primary_key)). The `.iteration` column contains the ID of the sample within a specific `.chain`.

In ArviZ, `draw` is equivalent to tidybayes's `.iteration`, _not_ tidybayes's `.draw`: it is the ID of the MCMC sample _within_ a `chain`.  Rather than create a single primary key column as tidybayes does, ArviZ instead uses `draw` and `chain` as a [composite primary key](https://en.wikipedia.org/wiki/Composite_key). We follow ArviZ conventions in PolarBayes.

# Other resources
## polars for tidyverse users
If you're familiar with tidybayes and the tidyverse but new to polars, consider a consulting a polars tutorial aimed at tidyverse users. We like [this one by Emily Riederer](https://www.emilyriederer.com/post/py-rgo-polars/).
