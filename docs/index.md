# PolarBayes

PolarBayes is a Python package for converting Bayesian inference output into ["tidy data"](https://tidyr.tidyverse.org/articles/tidy-data.html) format dataframes.

This package aims to be a spiritual Python port of the [tidybayes](https://mjskay.github.io/tidybayes/) package for the [R](https://www.r-project.org/) and [tidyverse](https://www.tidyverse.org/) ecosystem. It substitutes [polars](https://docs.pola.rs/user-guide/getting-started/) for the tidyverse and [ArviZ](https://python.arviz.org/en/stable/index.html) [`InferenceData`](https://python.arviz.org/en/stable/api/inference_data.html) objects for [`posterior::draws_df`](https://mc-stan.org/posterior/reference/draws_df.html) objects.


## Installation
You can install the development version of PolarBayes within an individual Python [project](https://docs.astral.sh/uv/concepts/projects/) (recommended) or within an [environment](https://docs.astral.sh/uv/pip/environments/) using any Python package management tool that supports `git` remotes, including [`uv`](https://docs.astral.sh/uv/), [`poetry`](https://python-poetry.org/), and [`pip`](https://pip.pypa.io/en/stable/index.html).

### Project level
=== "uv"

    ```shell
	uv add git+https://github.com/cdcgov/polarbayes.git
    ```

=== "poetry"

    ```shell
	poetry add git+https://github.com/cdcgov/polarbayes.git
    ```

### Environment level
=== "uv"

    ```shell
	uv pip install git+https://github.com/cdcgov/polarbayes.git
    ```

=== "pip"

    ```shell
	pip install git+https://github.com/cdcgov/polarbayes.git
    ```

## Getting Started
If you've used tidybayes before, jump right in with the [PolarBayes quickstart for tidybayes users](quickstart_for_tidybayes_users.md). A full tutorial that assumes no prior knowlege of tidybayes is [in progress](https://github.com/CDCgov/polarbayes/issues/37).
