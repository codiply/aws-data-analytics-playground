import typing
from benedict import benedict

class EnvironmentConfig():
    def __init__(self, config: benedict):
        self.config = config.clone()

    @property
    def environment_enabled(self):
        return self.config.get_bool('Environment.Enabled')

    @property
    def environment_name(self):
        return self.config['Environment.Name']

    @property
    def environment_short_name(self):
        return self.config['Environment.ShortName']

    @property
    def account_id(self):
        return self.config['Environment.AccountId']

    @property
    def region(self):
        return self.config['Environment.Region']

    @property
    def project(self):
        return self.config['Environment.Project']

    @property
    def resource_prefix(self):
        return f"{self.project}-{self.environment_short_name.lower()}"

    def for_sections(self, sections: typing.Sequence[str]):
        config = benedict()

        config['Environment'] = self.config['Environment']
        for section in sections:
            config[section] = self.config[section]

        return EnvironmentConfig(config)