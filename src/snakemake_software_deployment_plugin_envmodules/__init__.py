from typing import Iterable, Tuple
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
        self.names: Tuple[str] = names

    def identity_attributes(self) -> Iterable[str]:
        # The identity of the env spec is given by the names of the modules.
        yield "names"

    def source_path_attributes(self) -> Iterable[str]:
        # no paths involved here
        return ()


class Env(EnvBase):
    def __post_init__(self):
        # Check if the module command is available
        self.check()

    @EnvBase.once
    def check(self) -> None:
        if self.run_cmd("type module", stdout=sp.PIPE, stderr=sp.PIPE).returncode != 0:
            raise WorkflowError(
                "The module command is not available. "
                "Please make sure that the environment modules are "
                "available on your system."
            )

    def decorate_shellcmd(self, cmd: str) -> str:
        # Decorate given shell command such that it runs within the environment.
        # Unclear why that happens.
        # one might have to say 'shopt -s expand_aliases;', but that did not
        # help either...
        return f"module purge && module load {' '.join(self.spec.names)}; {cmd}"

    def record_hash(self, hash_object) -> None:
        # We just hash the names here as the best thing we can do for envmodules
        # for now. Ideally, the hash should change upon changes of what is deployed
        # in the env module.
        hash_object.update(",".join(self.spec.names).encode())

    def report_software(self) -> Iterable[SoftwareReport]:
        # An environment module is just a name, so we cannot report any software here?
        # TODO, maybe there is some way to get software from the module?
        return ()
