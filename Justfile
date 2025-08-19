BUILD_DIR := "build"
SRC_DIR := "src"

build:
    uv run ventoy-ng-cpio build

_docker_cache:
    @mkdir -p .local/var/docker/{uv_cache,uv_data,venv}

docker-build-image:
    docker compose build

docker-enter-image: _docker_cache
    docker compose run --rm builder

build-in-docker: _docker_cache
    docker compose run --rm builder just

clean:
    -rm -r {{BUILD_DIR}}/build-aux {{BUILD_DIR}}/output {{BUILD_DIR}}/work

clean-all:
    -rm -r {{BUILD_DIR}}

clean-dist: clean
    -rm -r {{BUILD_DIR}}/dist

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
        --extension-pkg-allow-list zstd \
        {{SRC_DIR}}
