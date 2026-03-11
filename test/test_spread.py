import arviz as az
import numpy as np
import pytest
import pandas as pd
import polars as pl
import polars.selectors as cs

from polarbayes.schema import order_index_column_names, CHAIN_NAME, DRAW_NAME

from polarbayes.spread import (
    spread_draws_to_pandas_,
    spread_draws,
    spread_draws_and_get_index_cols,
)

eight_schools_data = az.load_arviz_data("non_centered_eight")


spread_args_and_random_seeds = [
    [dict(var_names=["mu", "theta_t"]), None],
    [dict(num_samples=4), 42],
    [dict(filter_vars="like", var_names=["theta"]), None],
    [dict(filter_vars="regex", var_names=["(theta_t)|(mu)"]), None],
    [
        dict(
            filter_vars="regex",
            var_names="(theta_t)|(mu)",
            combined=False,
        ),
        None,
    ],
    [dict(), None],
]


def get_n_identical_rngs(seed, n):
    """
    Get a tuple of n identically parametrized
    numpy random number generators, or None
    if the seed is None.
    """
    if seed is None:
        return tuple([None] * n)
    else:
        return tuple(np.random.default_rng(seed) for _ in range(n))


@pytest.mark.parametrize(
    ["spread_args", "random_seed"], spread_args_and_random_seeds
)
def test_spread_to_pandas(spread_args, random_seed):
    """
    Test the spread_draws_to_pandas_ internal function
    is a light wrapper of az.extract with the expected properties.
    """
    random_seed_spread, random_seed_extract = get_n_identical_rngs(
        random_seed, 2
    )
    result = spread_draws_to_pandas_(
        eight_schools_data, **spread_args, random_seed=random_seed_spread
    )
    expected = az.extract(
        eight_schools_data,
        **spread_args,
        keep_dataset=True,
        random_seed=random_seed_extract,
    ).to_dataframe()

    assert isinstance(result, pd.DataFrame)
    assert result.equals(expected)
    # reserved names should always be present in index and never present as columns
    assert CHAIN_NAME in result.index.names
    assert DRAW_NAME in result.index.names
    assert CHAIN_NAME not in result.columns
    assert DRAW_NAME not in result.columns


@pytest.mark.parametrize(
    ["spread_args", "random_seed"], spread_args_and_random_seeds
)
def test_spread_draws_and_get_index_columns(spread_args, random_seed):
    random_seed_pl, random_seed_pd = get_n_identical_rngs(random_seed, 2)
    result_df, result_index = spread_draws_and_get_index_cols(
        eight_schools_data,
        **spread_args,
        random_seed=random_seed_pl,
    )
    pd_df = spread_draws_to_pandas_(
        eight_schools_data,
        **spread_args,
        random_seed=random_seed_pd,
    )

    # result index
    assert set(result_index) == set(pd_df.index.names)
    # result index should be returned already ordered according to the schema
    # and result columns should follow the same order.
    ordered_index = order_index_column_names(result_index)
    assert result_index == ordered_index
    expected_cols = (
        ordered_index
        + result_df.select(cs.exclude(result_index)).collect_schema().names()
    )
    assert result_df.columns == expected_cols

    assert result_df.equals(
        pl.DataFrame(pd_df.reset_index()).select(
            cs.by_name(ordered_index, require_all=True),
            cs.exclude(ordered_index),
        )
    )


@pytest.mark.parametrize(
    ["spread_args", "random_seed"], spread_args_and_random_seeds
)
def test_spread_wraps_spread_with_index(spread_args, random_seed):
    """
    spread_draws should be a light wrapper of
    spread_draws_and_get_index_cols and should
    agree with it.
    """
    random_seed_index, random_seed_no_index = get_n_identical_rngs(
        random_seed, 2
    )
    result, index = spread_draws_and_get_index_cols(
        eight_schools_data,
        **spread_args,
        random_seed=random_seed_index,
    )
    result_no_index = spread_draws(
        eight_schools_data,
        **spread_args,
        random_seed=random_seed_no_index,
    )
    assert result.equals(result_no_index)
    for col in index:
        assert col in result_no_index.columns
