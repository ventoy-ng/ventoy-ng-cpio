from .runtime.prepare import do_prepare
from .runtime.build import do_build
from .project import Project


def main():
    print("Hello from ventoy-ng-cpio!")

    proj = Project.load("project")
    #do_prepare(proj)
    do_build(proj)
