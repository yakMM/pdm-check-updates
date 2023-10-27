""""Quick and dirty pdm plugin to check for available updates from Pypi"""

import argparse

from packaging.version import parse
from pdm.cli.commands.base import BaseCommand
from pdm.core import Core
from pdm.project.core import Project


class CheckCommand(BaseCommand):
    """Check if some constraints can be updated"""

    def handle(self, project: Project, _: argparse.Namespace) -> None:
        for group in project.iter_groups():
            deps = project.get_dependencies(group)
            for dep in deps.values():
                if dep.is_pinned and not dep.is_vcs and not dep.is_file_or_url:
                    first = None
                    info = False
                    dep_version = parse(str(dep.specifier).replace("=", ""))
                    for candidate in project.get_repository()._find_candidates(
                        dep, minimal_version=False
                    ):
                        if not candidate.version:
                            raise ValueError(f"Invalid candidate: {candidate.name}")
                        version = parse(candidate.version)
                        if not version.is_prerelease or (
                            version.is_prerelease and dep_version.is_prerelease
                        ):
                            first = candidate
                            break
                        elif not info:
                            info = True
                            print(
                                f"Info: pre-release available for {dep.name}: {version}"
                            )
                    if not first:
                        raise ValueError(
                            f"No matching candidate found for package {dep.name}"
                        )
                    if first.version != str(dep_version):
                        print(
                            f"Package '{dep.name}' can be updated: "
                            f"'{dep_version}' => '{first.version}'"
                        )
                else:
                    first = next(
                        iter(
                            project.get_repository()._find_candidates(
                                dep, minimal_version=False
                            )
                        )
                    )
                    if not first.version:
                        raise ValueError(f"Invalid candidate: {first.name}")
                    version = parse(first.version)
                    print(f"Info: latest available version for {dep.name} is {version}")


def check(core: Core) -> None:
    core.register_command(CheckCommand, "check")
