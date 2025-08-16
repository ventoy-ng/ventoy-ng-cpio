from .projectv2.project import Project
from .runtime.build import do_build
from .runtime.prepare import do_prepare


def main():
    print("Hello from ventoy-ng-cpio!")

    proj = Project.load("project")
    do_prepare(proj)
    do_build(proj)
