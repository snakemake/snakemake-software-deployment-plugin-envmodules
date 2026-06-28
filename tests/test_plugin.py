import hashlib
import os
from types import SimpleNamespace
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


# ---------------------------------------------------------------------------
# Unit tests for EnvSpec and the pure Env methods.
#
# These raise test coverage and guard the fix that made
# identity_attributes / source_path_attributes classmethods (so that EnvSpec is
# hashable and usable as a dict key, which the software-deployment manager
# relies on for its specs_to_envs cache).
# ---------------------------------------------------------------------------


def _env_with_spec(spec):
    """An Env-like object with only `.spec` set.

    Env.__post_init__ runs check(), which needs the `module` command, so we
    bypass construction and exercise only methods that depend on self.spec.
    """
    return SimpleNamespace(spec=spec)


def _spec(*names):
    """Construct an EnvSpec the way the directive factory does (with technical_init).

    technical_init() is required before hashing/equality, because EnvSpecBase.__hash__
    reads managed attributes (e.g. self.kind) that it sets.
    """
    spec = EnvSpec(*names)
    spec.technical_init()
    return spec


def test_envspec_stores_names_as_tuple():
    assert _spec("bwa", "samtools").names == ("bwa", "samtools")


def test_envspec_str_is_comma_joined():
    assert str(_spec("bwa", "samtools")) == "bwa,samtools"
    assert str(_spec("bwa")) == "bwa"


def test_identity_attributes_yields_names():
    # classmethod: callable on the class itself
    assert list(EnvSpec.identity_attributes()) == ["names"]


def test_source_path_attributes_is_empty():
    assert list(EnvSpec.source_path_attributes()) == []


def test_envspec_hash_and_equality_use_names():
    # Regression guard: __hash__ resolves through cls.identity_attributes(),
    # which only works because identity_attributes is now a @classmethod.
    a = _spec("bwa", "samtools")
    b = _spec("bwa", "samtools")
    c = _spec("bwa")
    assert a == b
    assert hash(a) == hash(b)
    assert a != c
    assert hash(a) != hash(c)


def test_envspec_is_usable_as_dict_key():
    # The original crash: hashing an envmodules spec raised TypeError, so it
    # could not be used as a dict key (e.g. in specs_to_envs).
    spec = _spec("bwa")
    lookup = _spec("bwa")
    assert {spec: "env"}[lookup] == "env"


def test_env_decorate_shellcmd_loads_modules():
    env = _env_with_spec(_spec("bwa", "samtools"))
    assert Env.decorate_shellcmd(env, "echo hi") == (
        "module purge && module load bwa samtools && echo hi"
    )


def test_env_decorate_shellcmd_quotes_unsafe_names():
    env = _env_with_spec(_spec("name with space"))
    assert "module load 'name with space'" in Env.decorate_shellcmd(env, "cmd")


def test_env_record_hash_uses_names():
    env = _env_with_spec(_spec("bwa", "samtools"))
    h = hashlib.sha256()
    Env.record_hash(env, h)
    assert h.hexdigest() == hashlib.sha256(b"bwa,samtools").hexdigest()
