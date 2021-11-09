from ..config.environment import EnvironmentConfig


class ResourceNames():
    @staticmethod
    def bucket(config: EnvironmentConfig):
        return f"{config.resource_prefix}-{config.account_id}"
