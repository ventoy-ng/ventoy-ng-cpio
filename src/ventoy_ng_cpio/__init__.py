from .project import Project

def main() -> None:
    print("Hello from ventoy-ng-cpio!")

    proj = Project.load("project")
