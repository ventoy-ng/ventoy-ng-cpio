from argparse import ArgumentParser
from pathlib import Path
from typing import Optional

from ventoy_ng_cpio.config import CONFIG
from ventoy_ng_cpio.project.project import Project
from ventoy_ng_cpio.stages.build import do_build
from ventoy_ng_cpio.stages.prepare import do_prepare
# broken on purpose
from ventoy_ng_cpio.consts import BUILD_DIR, PROJECT_DIR


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
        "components",
        nargs="*",
    )
    parser_build.add_argument(
        "--target-filter",
        help="regex used to filter jobs idk i'm tired",
    )
    args = parser.parse_args()
    components: Optional[list[str]] = None
    if args.components:
        components = args.components

    CONFIG.cleanbuild = args.cleanbuild
    project = Project.load(args.project_dir, args.build_dir)

    match args.command:
        case "build":
            do_prepare(project)
            do_build(project, components, args.target_filter)
        case _:
            raise RuntimeError
