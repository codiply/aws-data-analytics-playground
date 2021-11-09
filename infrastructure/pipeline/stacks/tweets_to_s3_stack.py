from aws_cdk import core as cdk
from aws_cdk import aws_ecs as ecs
from aws_cdk import aws_s3 as s3

from ..config.environment import EnvironmentConfig
from ..constructs.event_firehose import EventFirehose


class TweetsToS3Stack(cdk.Stack):
    def __init__(self,
                 scope: cdk.Construct,
                 id: str,
                 config: EnvironmentConfig,
                 s3_bucket: s3.Bucket,
                 ecs_cluster: ecs.Cluster,
                 **kwargs) -> None:
        super().__init__(scope, id, **kwargs)

        self._config: EnvironmentConfig = config

        EventFirehose(
            self,
            'event-firehose',
            config.for_sections([]),
            s3_bucket=s3_bucket,
            event_name='tweets',
            path_prefix='tweets')  # TODO: pull this from config
