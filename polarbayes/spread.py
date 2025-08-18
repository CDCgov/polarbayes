from typing import Iterable

import arviz as az
import numpy as np
import pandas as pd
import polars as pl


def spread_draws_to_pandas_(
    data: az.InferenceData,
    group: str = "posterior",
    combined: bool = True,
    var_names: Iterable[str] = None,
    filter_vars: str = None,
    num_samples: int = None,
    rng: bool | int | np.random.Generator = None,
) -> pd.DataFrame:
    """
    Convert an ArviZ InferenceData object group to a Pandas
    DataFrame of tidy (spread) draws, using the syntax of
    arviz.extract

    Parameters
    ----------
    data
        Data to convert.

    group
        `group` parameter passed to `az.extract`.

    combined
        `combined` parameter passed to `az.extract`.

    var_names
        `var_names` parameter passed to `az.extract`.

    filter_vars
        `filter_vars` parameter passed to `az.extract`.

    num_samples
        `num_samples` parameter passed to `az.extract`.

    rng
        `rng` parameter passed to `az.extract`.

    Returns
    -------
    pd.DataFrame
       Pandas DataFrame with a MultiIndex on the chain id,
       draw id, and any additional indices determined by
       the dimensions of the variables selected via
       `var_names` or `filter_vars`, with columns containing
       the associated values of those variables.
    """
    df = az.extract(
        data,
        group=group,
        combined=combined,
        var_names=var_names,
        filter_vars=filter_vars,
        num_samples=num_samples,
        keep_dataset=True,
        rng=rng,
    ).to_dataframe()
    if combined:
        df = df.drop(["chain", "draw"], axis=1)
        # az.extract with combined=True assumes that the InferenceData
        # object has "chain" and "draw" named dimensions and errors otherwise.
        # When the resultant dataset is converted to a pandas dataframe
        # via .to_dataframe(), "chain" and "draw" are included _both_
        # as column names and as Pandas MultiIndex names.
        # See https://github.com/pydata/xarray/issues/10538
        #
        # We only want/need chain and draw in the MultiIndex,
        # so we drop the columns, which are guaranteed to exist
        # per by the az.extract assumption mentioned above.
    return df


def spread_draws_and_get_index_cols(
    data: az.InferenceData,
    group: str = "posterior",
    combined: bool = True,
    var_names: Iterable[str] = None,
    filter_vars: str = None,
    num_samples: int = None,
    rng: bool | int | np.random.Generator = None,
    enforce_drop_chain_draw: bool = False,
) -> tuple[pl.DataFrame, tuple]:
    """
    Convert an ArviZ InferenceData object to a polars
    DataFrame of tidy (spread) draws, using the syntax of
    arviz.extract. Return that DataFrame alongside a tuple
    giving the names of the DataFrame's index columns.

    Parameters
    ----------
    data
        Data to convert.

    group
        `group` parameter passed to `az.extract`.

    combined
        `combined` parameter passed to `az.extract`.

    var_names
        `var_names` parameter passed to `az.extract`.

    filter_vars
        `filter_vars` parameter passed to `az.extract`.

    num_samples
        `num_samples` parameter passed to `az.extract`.

    rng
        `rng` parameter passed to `az.extract`.

    Returns
    -------
    tuple[pl.DataFrame, tuple]
        Two-entry whose first entry is the DataFrame, and whose
        second entry is a tuple giving the names of that DataFrame's
        index columns. The DataFrame consists of columns named for
        variables and index columns. Columns named for variables
        contain the sampled values of those variables. Index columns
        include standard columns to identify a unique
        sample (typically `"chain"` and "draw"`) plus (as needed)
        columns that index array-valued variables.
    """

    df = spread_draws_to_pandas_(
        data,
        group=group,
        combined=combined,
        var_names=var_names,
        filter_vars=filter_vars,
        num_samples=num_samples,
        rng=rng,
    )
    if enforce_drop_chain_draw:
        df = df.drop(["chain", "draw"], axis=1)
        # this is handled automatically when `combined=True`
        # by spread_draws_to_pandas_,
        # but not when combined=False but the `data` input
        # is an already-combined output of `az.extract`.
    return (pl.DataFrame(df.reset_index()), tuple(df.index.names))


def spread_draws(
    data: az.InferenceData,
    group: str = "posterior",
    combined: bool = True,
    var_names: Iterable[str] = None,
    filter_vars: str = None,
    num_samples: int = None,
    rng: bool | int | np.random.Generator = None,
) -> pl.DataFrame:
    """
    Convert an ArviZ InferenceData object to a polars
    DataFrame of tidy (spread) draws, using the syntax of
    `arviz.extract`.

    Parameters
    ----------
    data
        Data to convert.

    group
        `group` parameter passed to `az.extract`.

    combined
        `combined` parameter passed to `az.extract`.

    var_names
        `var_names` parameter passed to `az.extract`.

    filter_vars
        `var_names` parameter passed to `az.extract`.

    num_samples
        `num_samples` parameter passed to `az.extract`.

    rng
        `rng` parameter passed to `az.extract`.

    Returns
    -------
    pl.DataFrame
        The DataFrame of tidy draws. Consists of columns named for
        variables and index columns. Columns named for variables
        contain the sampled values of those variables. Index columns
        include standard columns to identify a unique
        sample (typically `"chain"` and "draw"`) plus (as needed)
        columns that index array-valued variables.
    """
    result, _ = spread_draws_and_get_index_cols(
        data,
        group=group,
        combined=combined,
        var_names=var_names,
        filter_vars=filter_vars,
        num_samples=num_samples,
        rng=rng,
    )
    return result
