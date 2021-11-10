import typing
from benedict import benedict


class EnvironmentConfig:
    def __init__(self, config):
        self._config = config.clone()

    @property
    def environment_enabled(self) -> bool:
        return self._config.get_bool('Environment.Enabled')

    @property
    def environment_name(self) -> str:
        return self._config['Environment.Name']

    @property
    def environment_short_name(self) -> str:
        return self._config['Environment.ShortName']

    @property
    def account_id(self) -> str:
        return self._config['Environment.AccountId']

    @property
    def region(self) -> str:
        return self._config['Environment.Region']

    @property
    def needs_manual_approval(self) -> bool:
        return self._config.get_bool('Environment.NeedsManualApproval')

    @property
    def project(self) -> str:
        return self._config['Environment.Project']

    @property
    def resource_prefix(self) -> str:
        return f"{self.project}-{self.environment_short_name.lower()}"

    def section(self, key: str) -> benedict:
        return self._config[key]

    def for_sections(self, sections: typing.Sequence[str]):
        config = benedict()

        config['Environment'] = self._config['Environment']
        for section in sections:
            config[section] = self._config[section]

        return EnvironmentConfig(config)
