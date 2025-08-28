import arviz as az
import numpy as np
import pytest

from polarbayes.schema import CHAIN_NAME, DRAW_NAME

from polarbayes.spread import (
    spread_draws_to_pandas_,
    spread_draws,
    spread_draws_and_get_index_cols,
)

rugby_field_data = az.load_arviz_data("rugby_field")


spread_args_and_rngs = [
    [dict(var_names=["defs", "intercept"]), None],
    [dict(num_samples=4), 42],
    [dict(filter_vars="like", var_names=["def"]), None],
    [dict(filter_vars="regex", var_names=["(def)|(intercept)"]), None],
    [
        dict(
            filter_vars="regex",
            var_names=["(def)|(intercept)"],
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


@pytest.mark.parametrize(["spread_args", "rng_seed"], spread_args_and_rngs)
def test_spread_to_pandas(spread_args, rng_seed):
    """
    Test the spread_draws_to_pandas_ internal function
    is a light wrapper of az.extract with the expected properties.
    """
    rng_spread, rng_extract = get_n_identical_rngs(rng_seed, 2)
    result = spread_draws_to_pandas_(
        rugby_field_data, **spread_args, rng=rng_spread
    )
    expected = az.extract(
        rugby_field_data, **spread_args, rng=rng_extract
    ).to_dataframe()
    if spread_args.get("combined", True):
        expected = expected.drop([CHAIN_NAME, DRAW_NAME], axis=1)

    assert result.equals(expected)
    assert CHAIN_NAME in result.index.names
    assert DRAW_NAME in result.index.names
    assert CHAIN_NAME not in result.columns
    assert DRAW_NAME not in result.columns


@pytest.mark.parametrize(["spread_args", "rng_seed"], spread_args_and_rngs)
def test_spread_wraps_spread_with_index(spread_args, rng_seed):
    rng_index, rng_no_index = get_n_identical_rngs(rng_seed, 2)
    result, index = spread_draws_and_get_index_cols(
        rugby_field_data, **spread_args, rng=rng_index
    )
    result_no_index = spread_draws(
        rugby_field_data, **spread_args, rng=rng_no_index
    )
    assert result.equals(result_no_index)
    for col in index:
        assert col in result_no_index.columns
