import os
from typing import Dict, Optional

from .loader import Loader
from ..confz_source import ConfZEnvSource


class EnvLoader(Loader):
    """Config loader for environment variables."""

    @classmethod
    def _transform_name(cls, name: str):
        return name.lower().replace('-', '_')

    @classmethod
    def _transform_remap(cls, map_in: Optional[Dict[str, str]]) -> Optional[Dict[str, str]]:
        if map_in is None:
            return None

        map_out = dict()
        for key, value in map_in.items():
            map_out[cls._transform_name(key)] = value
        return map_out

    @classmethod
    def _check_allowance(cls, var_name: str, confz_source: ConfZEnvSource) -> bool:
        if not confz_source.allow_all:
            if confz_source.allow is None:
                return False

            allow_list = [cls._transform_name(var) for var in confz_source.allow]
            if var_name not in allow_list:
                return False

        if confz_source.deny is not None:
            deny_list = [cls._transform_name(var) for var in confz_source.deny]
            if var_name in deny_list:
                return False

        return True

    @classmethod
    def populate_config(cls, config: dict, confz_source: ConfZEnvSource):
        remap = cls._transform_remap(confz_source.remap)

        for env_var in os.environ:
            var_name = env_var
            if confz_source.prefix is not None:
                if not var_name.startswith(confz_source.prefix):
                    continue
                var_name = var_name[len(confz_source.prefix):]

            var_name = cls._transform_name(var_name)
            if not cls._check_allowance(var_name, confz_source):
                continue

            if remap is not None and var_name in remap:
                var_name = remap[var_name]

            config[var_name] = os.environ[env_var]