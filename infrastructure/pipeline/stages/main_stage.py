from aws_cdk import core as cdk

from ..config.environment import EnvironmentConfig
from ..stacks.data_lake_stack import DataLakeStack

class MainStage(cdk.Stage):
    def __init__(self, scope: cdk.Construct, id: str, config: EnvironmentConfig, **kwargs):
        super().__init__(scope, id, **kwargs)

        DataLakeStack(self, f"{config.resource_prefix}-data-lake", config.for_sections(['S3Bucket']))