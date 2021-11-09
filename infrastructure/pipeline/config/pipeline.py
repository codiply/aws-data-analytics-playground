import os
import typing
from benedict import benedict

from .environment import EnvironmentConfig


class PipelineConfig():
    def __init__(self, config_directory: str, pipeline_name: str = None):
        self.pipeline_name: str = pipeline_name if pipeline_name else "main"
        self._config = benedict(os.path.join(config_directory, f'{self.pipeline_name}.yaml'), format='yaml')

    def for_ci_cd_environment(self) -> dict:
        config = self._config['CiCdEnvironment'].clone()
        config['Project'] = self._config['Project']

        return config

    def for_environment(self, environment_name: str) -> EnvironmentConfig:
        environment_config = self._config[f'Environments.{environment_name}'].clone()
        environment_config['Project'] = self._config['Project']
        config_overrides = environment_config['ConfigOverrides']
        del environment_config['ConfigOverrides']

        config = self._config['GlobalConfig'].clone()
        config['Environment'] = environment_config
        if config_overrides:
            config.merge(config_overrides, overwrite=True)

        return EnvironmentConfig(config)

    def for_all_environments(self) -> typing.Generator[EnvironmentConfig, None, None]:
        environment: str
        for environment in self._config['Environments'].keys():
            yield self.for_environment(environment)
