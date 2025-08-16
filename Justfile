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
