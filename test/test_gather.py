import pytest
import arviz as az
import polars as pl
from polarbayes.gather import gather_draws


rugby_field_data = az.load_arviz_data("rugby_field")


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
    print(data)
    result = gather_draws(data, "posterior")
    data_vars = list(data.posterior.keys())
    # all and only variables from posterior group should
    # be present in the variable column
    assert all([v in result["variable"] for v in data_vars])
    assert result["variable"].is_in(data_vars).all()
    assert "chain" in result.columns
    assert "draw" in result.columns
    # chain and draw should never be null and should always
    # be ints
    assert result["chain"].dtype.is_integer()
    assert result["draw"].dtype.is_integer()
    assert result["chain"].is_not_null().all()
    assert result["draw"].is_not_null().any()

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
    pass
