from aws_cdk import core as cdk
from aws_cdk import aws_ecs as ecs
from aws_cdk import aws_s3 as s3
from benedict import benedict

from ..config.environment import EnvironmentConfig
from ..constructs.event_firehose import EventFirehose
from ..constructs.tweets_firehose_producer import TweetsFirehoseProducer


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

        event_firehose = EventFirehose(
            self,
            'event-firehose',
            config.for_sections(['EventFirehose']),
            s3_bucket=s3_bucket,
            event_name='tweets',
            path_prefix=config.section('Tweets')['S3PathPrefix'])

        tweets_firehose_producer_config: benedict = config.section('TweetsFirehoseProducer')

        if tweets_firehose_producer_config.get_bool('Enabled'):
            TweetsFirehoseProducer(
                self,
                'tweets-firehose-producer',
                config.for_sections(['Common', 'TweetsFirehoseProducer', 'TwitterApi']),
                ecs_cluster=ecs_cluster,
                delivery_stream=event_firehose.delivery_stream
            )
