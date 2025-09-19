import os
from typing import Optional, Type
from snakemake_interface_software_deployment_plugins import EnvBase, EnvSpecBase
from snakemake_interface_software_deployment_plugins.tests import (
    TestSoftwareDeploymentBase,
)
from snakemake_interface_software_deployment_plugins.settings import (
    SoftwareDeploymentSettingsBase,
)
from snakemake_software_deployment_plugin_envmodules import Env, EnvSpec

os.environ["MODULEPATH"] = "tests/modules"


class Test(TestSoftwareDeploymentBase):
    __test__ = True  # activate automatic testing
    shell_executable = ["bash", "-l", "-c"]

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
        return EnvSpec("somecmd")

    def get_settings_cls(self) -> Optional[Type[SoftwareDeploymentSettingsBase]]:
        # Return the settings class that should be used for this plugin.
        return None

    def get_settings(
        self,
    ) -> Optional[SoftwareDeploymentSettingsBase]:
        # If your plugin has settings, return a valid settings object here.
        # Otherwise, return None.
        return None

    def get_test_cmd(self) -> str:
        # Return a command that should be executable without error in the environment
        return "somecmd"
