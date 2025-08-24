# Install `just` to use this: https://just.systems/man/en/introduction.html

@_default:
    just --list --unsorted --justfile {{justfile()}}

[doc("Bootstrap the dev environment, checking for any dependencies we need")]
bootstrap:
    #!/usr/bin/env bash
    if ! uv --version >/dev/null 2>&1; then
        echo "You must install uv. We recommend one of:"
        echo " brew install uv"
        echo " pipx install uv"
        echo "Or if you don't have homebrew or pipx available in your environment, use the uv installer:"
        echo " curl -LsSf https://astral.sh/uv/install.sh | sh"
        exit 1
    fi

    # Install tox and tox-uv as tools...
    uv tool install --upgrade tox --with tox-uv

    uv tool install --upgrade pre-commit
    uv tool run pre-commit install

# Run a python script inside our venv
run *ARGS:
    uv run {{ARGS}}

test PKG="dist/*.whl" FACTOR="" *ARGS="": build
    uvx --with tox-uv tox run --installpkg {{PKG}} {{ if FACTOR != "" { "-f " + FACTOR } else {""} }} {{ARGS}}

check-lock *ARGS="":
    uv lock --locked {{ARGS}}

check-format *ARGS="":
    just run --only-group linting ruff format --check {{ARGS}}

fix-format *ARGS="":
    just run --only-group linting ruff format {{ARGS}}

check-lint *ARGS="":
    just run --only-group linting ruff check {{ARGS}}

fix-lint *ARGS="":
    just run --only-group linting ruff check --fix {{ARGS}}

check-types *ARGS="":
    # Rely on pyproject.toml configuration for source files
    just run --group type-checking mypy {{ARGS}}

check-coverage MIN="100" *ARGS="": test
    just run --only-group testing coverage combine
    just run --only-group testing coverage html --skip-covered --skip-empty
    just run --only-group testing coverage report --format=markdown
    just run --only-group testing coverage report --fail-under={{MIN}}


# Run all PR checks, as similar as possible to github actions
pr-checks: check-format check-lint check-types test

build *ARGS="":
    uv build {{ARGS}}

# Install venv with project's dependencies, removing unrelated packages
install *ARGS="--all-groups":
    uv sync {{ARGS}}

update *ARGS="":
    uv lock --upgrade {{ARGS}}

alias pr:=pr-checks

bump LVL="patch":
    uv version --bump {{LVL}}
