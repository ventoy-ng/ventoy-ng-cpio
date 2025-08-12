from .runtime.prepare import do_prepare
from .project import Project

def main():
    print("Hello from ventoy-ng-cpio!")

    proj = Project.load("project")
    do_prepare(proj)
