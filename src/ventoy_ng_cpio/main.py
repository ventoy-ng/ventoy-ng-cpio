from argparse import ArgumentParser
from pathlib import Path
from typing import Optional

from .config import CONFIG
from .consts import BUILD_DIR, PROJECT_DIR
from .projectv2.project import Project
from .runtime.build import do_build
from .runtime.prepare import do_prepare


def main():
    parser = ArgumentParser()
    parser.add_argument(
        "--project-dir",
        default=PROJECT_DIR,
        type=Path,
    )
    parser.add_argument(
        "--build-dir",
        default=BUILD_DIR,
        type=Path,
    )
    parser.add_argument(
        "--cleanbuild",
        action="store_true",
    )
    subparsers = parser.add_subparsers(dest="command", required=True)
    parser_build = subparsers.add_parser("build")
    parser_build.add_argument(
        "target_components",
        nargs="*",
    )
    args = parser.parse_args()
    target_components: Optional[list[str]] = None
    if args.target_components:
        target_components = args.target_components

    CONFIG.cleanbuild = args.cleanbuild
    project = Project.load(args.project_dir, args.build_dir)

    match args.command:
        case "build":
            do_prepare(project)
            do_build(project, target_components)
        case _:
            raise RuntimeError
