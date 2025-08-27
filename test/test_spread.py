import arviz as az
import numpy as np
import pytest

from polarbayes.spread import spread_draws, spread_draws_and_get_index_cols

rugby_field_data = az.load_arviz_data("rugby_field")

spread_args_and_rngs = [
    [dict(var_names=["defs", "intercept"]), None],
    [dict(num_samples=4), 42],
    [dict(filter_vars="like", var_names=["def"]), None],
    [dict(filter_vars="regex", var_names=["(def)|(intercept)"]), None],
    [dict(), None],
]


@pytest.mark.parametrize(["spread_args", "rng_seed"], spread_args_and_rngs)
def test_spread_wraps_spread_with_index(spread_args, rng_seed):
    if rng_seed is not None:
        rng_index = np.random.default_rng(rng_seed)
        rng_no_index = np.random.default_rng(rng_seed)
    else:
        rng_index, rng_no_index = None, None
    result, index = spread_draws_and_get_index_cols(
        rugby_field_data, **spread_args, rng=rng_index
    )
    result_no_index = spread_draws(
        rugby_field_data, **spread_args, rng=rng_no_index
    )
    assert result.equals(result_no_index)
    for col in index:
        assert col in result_no_index.columns
