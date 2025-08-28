import copy

import arviz as az
import numpy as np
import polars as pl
import pytest

from polarbayes.gather import (
    gather_draws,
    gather_variables,
    _assert_not_in_index_columns,
)
from polarbayes.schema import CHAIN_NAME, DRAW_NAME, VALUE_NAME, VARIABLE_NAME

rugby_field_data = az.load_arviz_data("rugby_field")


def assert_gathered_draws_as_expected(
    gathered_draws,
    variables,
    index_variables,
    variable_name=VARIABLE_NAME,
    value_name=VALUE_NAME,
):
    """
    Helper function for general expectations on the output of a
    gather_draws() calls.
    """
    assert isinstance(gathered_draws, pl.DataFrame)
    # all and only variables targeted should be present in the
    # variable column of the gathered dataframe.
    assert variable_name in gathered_draws.columns
    assert value_name in gathered_draws.columns
    assert all([v in gathered_draws["variable"] for v in variables])
    assert gathered_draws[variable_name].is_in(variables).all()
    assert CHAIN_NAME in gathered_draws.columns
    assert DRAW_NAME in gathered_draws.columns
    # chain and draw should never be null and should always
    # be ints
    assert gathered_draws[CHAIN_NAME].is_not_null().all()
    assert gathered_draws[DRAW_NAME].is_not_null().all()
    assert gathered_draws[CHAIN_NAME].dtype.is_integer()
    assert gathered_draws[DRAW_NAME].dtype.is_integer()

    # order of columns should be "chain", "draw", <index columns, alphabetically>,
    # <variable name>, <value name>
    assert gathered_draws.columns == [CHAIN_NAME, DRAW_NAME] + sorted(
        list(index_variables)
    ) + [
        variable_name,
        value_name,
    ]


@pytest.mark.parametrize(
    "arg_name", ["x", "a long name with spaces", "a_name%with_characters"]
)
@pytest.mark.parametrize("arg_value", ["test", "531a", "a_different_value"])
def test_assert_not_in_index(arg_name, arg_value):
    """
    Test the _assert_not_in_index_columns function
    raises the expected error iff required.
    """
    rng = np.random.default_rng(5)
    index_cols = [str(x) for x in rng.random(10)]
    with pytest.raises(
        ValueError, match=f"Specified {arg_name}='{arg_value}'"
    ):
        _assert_not_in_index_columns(
            arg_name, arg_value, index_cols + [arg_value]
        )
    no_raise = _assert_not_in_index_columns(arg_name, arg_value, index_cols)
    assert no_raise is None


@pytest.mark.parametrize(
    ["data", "index_cols"],
    [
        [
            pl.DataFrame(
                dict(x=range(10), y="c", z=[str(x) for x in range(5, 15)])
            ),
            ["x", "y"],
        ],
        [
            pl.LazyFrame(
                dict(x=range(10), y="c", z=[str(x) for x in range(5, 15)])
            ),
            ["x", "y"],
        ],
        [
            pl.LazyFrame(
                dict(
                    x=range(10),
                    y="c",
                    z=[str(x) for x in range(5, 15)],
                    chain=range(10),
                    draw=range(10),
                )
            ),
            None,
        ],
    ],
)
@pytest.mark.parametrize("variable_name", [None, VARIABLE_NAME, "custom_name"])
@pytest.mark.parametrize("value_name", [None, VALUE_NAME, "custom_name_2"])
def test_gather_variables_wraps_unpivot(
    data, index_cols, variable_name, value_name
):
    """
    Test that the gather_variables() function
    lightly wraps the Polars unpivot operation.
    """
    if index_cols is None:
        index_unpivot = [CHAIN_NAME, DRAW_NAME]
    else:
        index_unpivot = index_cols
    if variable_name is None:
        variable_name_unpivot = VARIABLE_NAME
    else:
        variable_name_unpivot = variable_name
    if value_name is None:
        value_name_unpivot = VALUE_NAME
    else:
        value_name_unpivot = value_name

    expected = data.unpivot(
        index=index_unpivot,
        variable_name=variable_name_unpivot,
        value_name=value_name_unpivot,
    )
    actual = gather_variables(
        data,
        index=index_cols,
        variable_name=variable_name,
        value_name=value_name,
    )

    # LazyFrames should not be instantiated by this call.
    assert isinstance(actual, type(data))

    # but instantiated frames should be equivalent
    if isinstance(actual, pl.LazyFrame):
        actual = actual.collect()
    if isinstance(expected, pl.LazyFrame):
        expected = expected.collect()
    assert actual.equals(expected)


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
    index_vars = set(
        i_col
        for index_col_dict in test_vars.values()
        for i_col in index_col_dict.keys()
    )
    # all and only variables from posterior group should
    # be present in the variable column
    assert_gathered_draws_as_expected(result, data_vars, index_vars)

    # variables not indexed by a given column should have null values for that index column
    # while those that are should have non-null values
    for var, index_col_dict in test_vars.items():
        df_filt = result.filter(pl.col("variable") == var)
        assert df_filt.height > 0
        for i_col, is_used in index_col_dict.items():
            col = df_filt.get_column(i_col)
            if is_used:
                assert col.is_not_null().all()
            else:
                assert col.is_null().all()


@pytest.mark.parametrize(
    ["data", "var_names", "expected_indices"],
    [
        (rugby_field_data, ["sd_def_field"], []),
        (rugby_field_data, ["intercept", "sd_def_field"], ["field"]),
        (rugby_field_data, ["defs", "sd_def_field"], ["team", "field"]),
    ],
)
def test_gather_does_not_create_unneeded_indices(
    data, var_names, expected_indices
):
    """
    Test that gather_draws() only creates index
    columns if one of the variables needs them.
    """
    result = gather_draws(data, "posterior", var_names=var_names)
    assert_gathered_draws_as_expected(result, var_names, expected_indices)


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
    )
    index_vars = ["team", "field"]

    # union of all types is string
    result_all = gather_draws(dat, "posterior")
    data_vars = list(dat.posterior.keys())
    assert_gathered_draws_as_expected(result_all, data_vars, index_vars)
    assert result_all["value"].dtype == pl.String

    # union of int and float is float
    result_float = gather_draws(
        dat, "posterior", var_names=["intercept", "intercept_int", "defs_int"]
    )
    assert_gathered_draws_as_expected(
        result_float, ["intercept", "intercept_int", "defs_int"], index_vars
    )
    assert result_float["value"].dtype.is_float()

    # if only integers are extracted, should be integers
    result_int = gather_draws(
        dat, "posterior", var_names=["intercept_int", "defs_int"]
    )
    assert_gathered_draws_as_expected(
        result_int, ["intercept_int", "defs_int"], index_vars
    )
    assert result_int["value"].dtype.is_integer()
