import pytest
import arviz as az
from polarbayes.gather import gather_draws


@pytest.fixture
def rugby_data():
    return az.load_arviz_data("rugby")


def test_gather_mixed_indices(rugby_data):
    """
    Test that `gather_draws()` handles
    mixed indices gracefully, with null
    where a variable is not indexed
    """
    result = gather_draws(rugby_data, "posterior")
    data_vars = list(rugby_data.posterior.keys())
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
    assert not result["chain"].is_null().any()
    assert not result["draw"].is_null().any()


def test_gather_mixed_types():
    """
    Test that gather_draws handles mixed
    types of variables to gather gracefully.
    """
    pass
