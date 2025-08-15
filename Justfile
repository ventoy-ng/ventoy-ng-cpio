build:
    uv run ventoy-ng-cpio

clean:
    -rm -r build/build-aux build/output build/work

clean-dist: clean
    -rm -r build/dist

clean-all:
    -rm -r build
