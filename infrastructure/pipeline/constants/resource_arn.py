from ..config.environment import EnvironmentConfig


class ResourceArn():
    @staticmethod
    def bucket(config: EnvironmentConfig):
        return f"{config.resource_prefix}-{config.account_id}"
