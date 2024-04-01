from typing import Callable

from cleo.commands.command import Command as CleoCommand
from cleo.helpers import option
from poetry.plugins.application_plugin import (
    ApplicationPlugin as PoetryApplicationPlugin,
)

from vet.commands import Commands


def get_available_commands():
    return [
        command_name
        for command_name in dir(Commands)
        if not command_name.startswith("_")
    ]


class VetInitCommand(CleoCommand):
    name = "vet init"
    description = "Initialize vet configuration."

    def handle(self) -> int:
        commands = Commands()
        commands.init()
        return 0


class VetLockCommand(CleoCommand):
    name = "vet lock"
    description = "Update the lock file with imported audits."

    def handle(self) -> int:
        commands = Commands()
        commands.lock()
        return 0


class VetCheckCommand(CleoCommand):
    name = "vet check"
    description = "Verify trust in project dependencies."

    options = [
        option(
            "safe-to-deploy",
            short_name="d",
            description="Whether to vet dependencies as 'safe to deploy' instead of 'safe to run'.",
            flag=True,
        )
    ]

    def handle(self) -> int:
        commands = Commands()

        check_safe_to_deploy = self.option("safe-to-deploy")
        failed_audits = commands.check(check_safe_to_deploy=check_safe_to_deploy)
        return int(bool(failed_audits))


class VetCommand(VetCheckCommand):
    name = "vet"


COMMANDS = [
    VetCommand,
    VetCheckCommand,
    VetInitCommand,
    VetLockCommand,
]


def _load(command: Callable[[], CleoCommand]) -> Callable[[], CleoCommand]:
    def _():
        return command()

    return _


class VetPoetryApplicationPlugin(PoetryApplicationPlugin):
    def activate(self, application):
        for command in COMMANDS:
            application.command_loader.register_factory(command.name, _load(command))
