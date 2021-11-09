from ..config.environment import EnvironmentConfig
from .resource_names import ResourceNames


class ResourceArn():
    @staticmethod
    def bucket(config: EnvironmentConfig):
        return f"arn:aws:s3::{ResourceNames.bucket(config)}"
