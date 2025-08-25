import copy

import arviz as az
import polars as pl
import pytest

from polarbayes.gather import gather_draws

rugby_field_data = az.load_arviz_data("rugby_field")


def assert_gathered_draws_as_expected(gathered_draws, variables):
    """
    Helper function for general expectations on the output of a
    gather_draws() calls.
    """
    assert isinstance(gathered_draws, pl.DataFrame)
    # all and only variables targeted should be present in the
    # variable column of the gathered dataframe.
    assert all([v in gathered_draws["variable"] for v in variables])
    assert gathered_draws["variable"].is_in(variables).all()
    assert "chain" in gathered_draws.columns
    assert "draw" in gathered_draws.columns
    # chain and draw should never be null and should always
    # be ints
    assert gathered_draws["chain"].is_not_null().all()
    assert gathered_draws["draw"].is_not_null().any()
    assert gathered_draws["chain"].dtype.is_integer()
    assert gathered_draws["draw"].dtype.is_integer()


@pytest.mark.parametrize(
    ["data", "test_vars"],
    [
        [
            rugby_field_data,
            {
                "intercept": {"team": False, "field": True},
                "defs": {"team": True, "field": True},
                "sd_def_field": {"team": False, "field": False},
            },
        ]
    ],
)
def test_gather_mixed_indices(data, test_vars):
    """
    Test that `gather_draws()` handles
    mixed indices gracefully, with null
    where a variable is not indexed
    """
    result = gather_draws(data, "posterior")
    data_vars = list(data.posterior.keys())
    # all and only variables from posterior group should
    # be present in the variable column
    assert_gathered_draws_as_expected(result, data_vars)

    # variables not indexed by a given column should have null values for that index column
    # while those that are should have non-null values
    for var, index_col_dict in test_vars.items():
        df_filt = result.filter(pl.col("variable") == var)
        assert df_filt.height > 0
        for i_col, is_used in index_col_dict.items():
            assert i_col in result.columns
            col = df_filt.get_column(i_col)
            if is_used:
                assert col.is_not_null().all()
            else:
                assert col.is_null().all()


def test_gather_mixed_types():
    """
    Test that gather_draws handles mixed
    types of variables to gather gracefully.
    """
    dat = copy.deepcopy(rugby_field_data)
    dat.posterior["intercept_int"] = (
        dat.posterior["intercept"].round().astype("int")
    )
    dat.posterior["defs_int"] = dat.posterior["defs"].round().astype("int")
    dat.posterior["intercept_string"] = dat.posterior["intercept"].astype(
        "str"
    assert result_all["value"].dtype == pl.String

    # union of all types is string
    result_all = gather_draws(dat, "posterior")
    data_vars = list(dat.posterior.keys())
    assert_gathered_draws_as_expected(result_all, data_vars)
    assert result_all["value"].dtype.is_(pl.String)

    # union of string and float is float
    result_float = gather_draws(
        dat, "posterior", var_names=["intercept", "intercept_int", "defs_int"]
    )
    assert_gathered_draws_as_expected(
        result_float, ["intercept", "intercept_int", "defs_int"]
    )
    assert result_float["value"].dtype.is_float()

    # if only integers are extracted, should be integers
    result_int = gather_draws(
        dat, "posterior", var_names=["intercept_int", "defs_int"]
    )
    assert_gathered_draws_as_expected(
        result_int, ["intercept_int", "defs_int"]
    )
    assert result_int["value"].dtype.is_integer()
