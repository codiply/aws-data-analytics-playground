from aws_cdk import core as cdk

from ..config.environment import EnvironmentConfig
from ..stacks.common_stack import CommonStack


class MainStage(cdk.Stage):
    def __init__(self, scope: cdk.Construct, id: str, config: EnvironmentConfig, **kwargs):
        super().__init__(scope, id, **kwargs)

        CommonStack(self, f"{config.resource_prefix}-common", config.for_sections(['S3Bucket', 'Vpc']))
