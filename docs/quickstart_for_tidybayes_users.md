# PolarBayes quickstart for tidybayes users

If you have used tidybayes before, PolarBayes should feel familiar. The key functions are still named [`spread_draws`][polarbayes.spread.spread_draws] and [`gather_draws`][polarbayes.gather.gather_draws], and they still yield tidy data frames indexed by MCMC draw, with additional index columns for array-valued parameters. This quickstart walks you through the key differences between the two packages' APIs, and the reasons they arise.

Most differences ultimately stem from the fact that PolarBayes is built on top of [ArviZ](https://python.arviz.org/en/stable/) and aims to wrap or mirror ArviZ's API and conventions to the extent possible.

Both [`spread_draws`][polarbayes.spread.spread_draws] and [`gather_draws`][polarbayes.gather.gather_draws] call [`arviz.extract`][] to get MCMC samples. They accept all the configuration that `extract`  permits, so it is worth reading the [`extract` docs and examples][`arviz.extract`] to get a sense of what is possible.

To get started, just provide list of variables to spread or gather as the `var_names` argument:

```python
import polarbayes as pb

pb.spread_draws(idata, var_names=["var1", "var2"])
pb.gather_draws(idata, var_names=["var1", "var2"])

```

Or provide no `var_names` to spread or gather all available variables:

```python
pb.spread_draws(idata)
pb.gather_draws(idata)
```


## Key differences between tidybayes and PolarBayes

### `InferenceData` groups
PolarBayes extracts tidy data frames from MCMC output stored in an [`arviz.InferenceData`][]  object. The tidybayes equivalent is the [`posterior::draws_df`](https://mc-stan.org/posterior/reference/draws_df.html) format. Unlike [`draws_df`](https://mc-stan.org/posterior/reference/draws_df.html) objects, [`InferenceData`][`arviz.InferenceData`] objects are organized into ["groups"](https://python.arviz.org/en/latest/getting_started/XarrayforArviZ.html#xarray-for-arviz) representing different categories of Bayesian input and output: `posterior` for posterior samples, `posterior_predictive` for posterior predictive draws, `prior_predictive` for prior predictive draws, et cetera.

[`spread_draws`][polarbayes.spread.spread_draws] and [`gather_draws`][polarbayes.gather.gather_draws] can extract draws from any appropriate group. If no group is specified, they default to extracting from the `posterior` group.

### No dots in column names

Reserved column names in tidybayes output begin with dots (`.`): `.chain`, `.iteration`, `.draw`, `.variable`, and `.value`. PolarBayes avoids dots in variable names because dots have a special role in Python syntax. Python is [object-oriented](https://en.wikipedia.org/wiki/Object-oriented_programming). In Python, as in many object-oriented programming languages, dots are used to access "attributes" and "methods" associated to particular objects.

NOTE: As you may know, R also has object-oriented features. The equivalent R operator to the python dot (`.`) is the dollar sign (`$`). You may have written `df$.draw` to retrieve a column named `.draw` from a data frame named `df`. So a polars column name like `.draw` is potentially a bad idea in the same way that a data frame column name like `$draw` could be a bad idea in R.

In PolarBayes, we instead reserve the bare column names `chain` and `draw` for indexing, consistent with ArviZ conventions for indexing MCMC output. If you try to extract variables with those name names from an [`arviz.InferenceData`][] object, PolarBayes will error and suggest renaming those variables prior to extraction.

Similarly, the default [`gather_draws`][polarbayes.gather.gather_draws] variable and value column names are `variable` and `value`. The columns can be given alternative, custom values using the `value_name` and `variable_name` keyword arguments, respectively.
.


### `draw` in PolarBayes corresponds to `.iteration` in tidybayes (_not_ `.draw`!)
In `tidybayes`, the `.draw` column contains the unique ID of an MCMC sample across all chains (in relational database terms, it is a [single column "primary key"](https://en.wikipedia.org/wiki/Primary_key)). The `.iteration` column contains the ID of the sample within a specific `.chain`.

In ArviZ, `draw` is equivalent to tidybayes's `.iteration`, and _not_ tidybayes's `.draw`; it is the ID of the MCMC sample _within_ a `chain`. Rather than create a single primary key column as tidybayes does, ArviZ instead uses `draw` and `chain` as a [composite primary key](https://en.wikipedia.org/wiki/Composite_key). Here too we follow ArviZ conventions in PolarBayes.

### Dimension names are automatic
Array-valued parameters are stored in [`InferenceData`][arviz.InferenceData] objects with named dimensions. [`spread_draws`][polarbayes.spread.spread_draws] and [`gather_draws`][polarbayes.gather.gather_draws] respect those named dimensions. As a result, you cannot (but also do not need to) name the dimensions of array-valued variables when requesting them in a spread or gather call.

So this tidybayes R code:
```R
draws <- mcmc_output |> spread_draws(x1[time], x2[time, location])
```

might become this PolarBayes Python code:

```python
draws = pb.spread_draws(mcmc_output_arviz, var_names = ["x1", "x2"])
```

The PolarBayes output will still have `time` and `location` columns along with the MCMC sample ID columns, provided those are the names of the dimensions in the `mcmc_output_arviz` [`InferenceData`][arviz.InferenceData] object. If the dimension names in your [`InferenceData`][arviz.InferenceData] object are not the ones you want in your output data frame, you can simply rename them via [`polars.DataFrame.rename`][].

### Dimension index conversion deferred to ArviZ
For similar reasons, PolarBayes does not provide functionality equivalent to tidybayes's [`recover_types()`](https://mjskay.github.io/tidybayes/reference/recover_types.html) converting integer indexes for array-valued MCMC output into more interpretable quantities (e.g. named categories, timestamps, geographic coordinates). PolarBayes instead relies on ArviZ's built-in functionality for dimension indexing.

ArviZ performs [`recover_types()`](https://mjskay.github.io/tidybayes/reference/recover_types.html)-like operations when [creating `InferenceData` objects](https://python.arviz.org/en/stable/getting_started/CreatingInferenceData.html) from probabilistic programming language (PPL) MCMC output. The degree and sophistication depends on the source PPL and what metadata it provides. ArviZ also has functionality for doing [manual dimension annotation](https://python.arviz.org/en/stable/api/generated/arviz.InferenceData.assign_coords.html).


# Other resources

## polars for tidyverse users
If you're familiar with tidybayes and the tidyverse but new to polars, consider a consulting a polars tutorial aimed at tidyverse users. We like [this one by Emily Riederer](https://www.emilyriederer.com/post/py-rgo-polars/).

## ArviZ and xarray documentation
It is worth consulting the [ArviZ documentation](https://python.arviz.org/en/stable/). ArviZ is built on top of a multi-dimensional array library called [xarray](https://docs.xarray.dev/en/stable/). The [xarray docs](https://docs.xarray.dev/en/stable/) are also helpful for learning ArviZ.
