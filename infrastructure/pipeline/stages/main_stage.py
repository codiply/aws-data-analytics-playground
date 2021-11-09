from aws_cdk import core as cdk

from ..config.environment import EnvironmentConfig
from ..stacks.common_stack import CommonStack
from ..stacks.tweets_to_s3_stack import TweetsToS3Stack


class MainStage(cdk.Stage):
    def __init__(self, scope: cdk.Construct, id: str, config: EnvironmentConfig, **kwargs):
        super().__init__(scope, id, **kwargs)

        common_stack = CommonStack(
            self,
            f"{config.resource_prefix}-common",
            config.for_sections(['EcsCluster', 'S3Bucket', 'Vpc']))

        TweetsToS3Stack(
            self,
            f"{config.resource_prefix}-tweets-to-s3",
            config=config.for_sections([]),
            s3_bucket=common_stack.s3_bucket,
            ecs_cluster=common_stack.ecs_cluster)
