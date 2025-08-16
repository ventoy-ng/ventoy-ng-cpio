BUILD_DIR := "build"
SRC_DIR := "src"

build:
    uv run ventoy-ng-cpio

clean:
    -rm -r {{SRC_DIR}}/build-aux {{SRC_DIR}}/output {{SRC_DIR}}/work

clean-all:
    -rm -r {{SRC_DIR}}

clean-dist: clean
    -rm -r {{SRC_DIR}}/dist

clean-pycache:
    -find {{SRC_DIR}} -iname __pycache__ -exec rm -r {} +

check: mypy pylint flake8

alias fmt := flake8
alias flake := flake8
alias lint := pylint
alias typecheck := mypy

flake8:
    -uv run flake8 {{SRC_DIR}}

isort:
    -uv run isort {{SRC_DIR}}

mypy:
    -uv run mypy {{SRC_DIR}}

pylint:
    -uv run pylint \
        --disable C0114,C0115,C0116 \
        {{SRC_DIR}}
