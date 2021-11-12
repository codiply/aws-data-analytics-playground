from aws_cdk import core as cdk

from ..config.environment import EnvironmentConfig
from ..stacks.base_stack import BaseStack
from ..stacks.common_stack import CommonStack
from ..stacks.tweets_to_s3_stack import TweetsToS3Stack


class MainStage(cdk.Stage):
    def __init__(self, scope: cdk.Construct, id: str, config: EnvironmentConfig, **kwargs):
        super().__init__(scope, id, **kwargs)

        base_stack: BaseStack = BaseStack(
            self,
            f"{config.resource_prefix}-base",
            config.for_sections(['S3Bucket'])
        )

        common_stack: CommonStack = CommonStack(
            self,
            f"{config.resource_prefix}-common",
            config.for_sections(['EcsCluster',
                                 'Vpc']))

        TweetsToS3Stack(
            self,
            f"{config.resource_prefix}-tweets-to-s3",
            config=config.for_sections([
                'Common',
                'EventFirehose',
                'Tweets',
                'TweetsFirehoseProducer',
                'TwitterApi']),
            s3_bucket=base_stack.s3_bucket,
            ecs_cluster=common_stack.ecs_cluster)
