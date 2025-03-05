import os
from typing import Optional, Type
from snakemake_interface_software_deployment_plugins import EnvBase
from snakemake_interface_software_deployment_plugins.tests import (
    TestSoftwareDeploymentBase,
)
from snakemake_interface_software_deployment_plugins.settings import (
    SoftwareDeploymentSettingsBase,
)
from snakemake_software_deployment_plugin_envmodules import Env, EnvSpec, EnvSpecBase

os.environ["MODULEPATH"] = "tests/modules"


class TestSoftwareDeployment(TestSoftwareDeploymentBase):
    __test__ = True  # activate automatic testing

    def get_software_deployment_provider_settings(
        self,
    ) -> Optional[SoftwareDeploymentSettingsBase]:
        return None

    def get_env_cls(self) -> Type[EnvBase]:
        return Env

    def get_env_spec(self) -> EnvSpecBase:
        # Return an env spec.
        # If the software deployment provider does not support deployable environments,
        # this method should return an existing environment spec that can be used for
        # testing.
        return EnvSpec(names=["somecmd"], within=None)

    def get_test_cmd(self) -> str:
        # Return a command that should be executable without error in the environment
        return "somecmd"
