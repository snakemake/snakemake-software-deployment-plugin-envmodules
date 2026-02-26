import shlex
from typing import Iterable
from pathlib import Path
import subprocess as sp
from snakemake_interface_software_deployment_plugins import (
    EnvBase,
    EnvSpecBase,
    SoftwareReport,
)
from snakemake_interface_common.exceptions import WorkflowError
from snakemake_interface_software_deployment_plugins.settings import CommonSettings


common_settings = CommonSettings(provides="envmodules")


class EnvSpec(EnvSpecBase):
    def __init__(self, *names: str):
        super().__init__()
        self.names: tuple[str, ...] = tuple(names)

    def identity_attributes(self) -> Iterable[str]:
        # The identity of the env spec is given by the names of the modules.
        yield "names"

    def source_path_attributes(self) -> Iterable[str]:
        # no paths involved here
        return ()

    def __str__(self) -> str:
        return ",".join(self.names)


class Env(EnvBase):
    spec: EnvSpec

    def __post_init__(self):
        # Check if the module command is available
        self.check()

    @EnvBase.once
    def check(self) -> None:
        res = self.run_cmd("type module", stdout=sp.PIPE, stderr=sp.STDOUT)
        if res.returncode != 0:
            raise WorkflowError(
                "The module command is not available. "
                "Please make sure that environment modules are "
                f"available on your system: {res.stdout.decode()}"
            )

    def decorate_shellcmd(self, cmd: str) -> str:
        # Decorate given shell command such that it runs within the environment.
        # Unclear why that happens.
        # one might have to say 'shopt -s expand_aliases;', but that did not
        # help either...
        return f"module purge && module load {' '.join(shlex.quote(name) for name in self.spec.names)} && {cmd}"

    def contains_executable(self, executable: str) -> bool:
        path = (
            self.run_cmd(
                self.decorate_shellcmd("echo $PATH"), capture_output=True, check=True
            )
            .stdout.decode()
            .split(":")[0]
        )
        return (Path(path) / executable).exists()

    def record_hash(self, hash_object) -> None:
        # We just hash the names here as the best thing we can do for envmodules
        # for now. Ideally, the hash should change upon changes of what is deployed
        # in the env module.
        hash_object.update(",".join(self.spec.names).encode())

    def report_software(self) -> Iterable[SoftwareReport]:
        # An environment module is just a name, so we cannot report any software here?
        # TODO, maybe there is some way to get software from the module?
        return ()
