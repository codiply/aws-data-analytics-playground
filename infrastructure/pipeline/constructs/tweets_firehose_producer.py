import typing

from aws_cdk import core as cdk
from aws_cdk import aws_iam as iam
from aws_cdk import aws_kinesisfirehose as firehose
from aws_cdk import aws_kms as kms

from ..config.environment import EnvironmentConfig
from benedict import benedict


class TweetsFirehoseProducer(cdk.Construct):
    def __init__(self,
                 scope: cdk.Construct,
                 id: str,
                 config: EnvironmentConfig,
                 delivery_stream: firehose.DeliveryStream):
        super().__init__(scope, id)

        self._twitter_api_config: benedict = config.section('TwitterApi')
        self._tweets_firehose_producer_config: benedict = config.section('TweetsFirehoseProducer')
        self._delivery_stream: firehose.DeliveryStream = delivery_stream

        policy_statements: typing.Sequence[iam.PolicyStatement] = self.define_task_role_policy_statements()

        environment = {
            'TWITTER_API_CONSUMER_KEY_SSM_PARAMETER': self._twitter_api_config['ConsumerKeySsmParameter'],
            'TWITTER_API_CONSUMER_SECRET_SSM_PARAMETER': self._twitter_api_config['ConsumerSecretSsmParameter'],
            'TWITTER_API_ACCESS_TOKEN_SSM_PARAMETER': self._twitter_api_config['AccessTokenSsmParameter'],
            'TWITTER_API_ACCESS_TOKEN_SECRET_SSM_PARAMETER': self._twitter_api_config['AccessTokenSecretSsmParameter'],
            'TWEETS_FILTER': self._tweets_firehose_producer_config['Filter'],
            'DELIVERY_STREAM_NAME': delivery_stream.delivery_stream_name
        }

    def define_task_role_policy_statements(self) -> typing.Sequence[iam.PolicyStatement]:
        parameter_arn_prefix = f"arn:aws:ssm:{cdk.Aws.REGION}:{cdk.Aws.ACCOUNT_ID}:parameter"
        return [
            iam.PolicyStatement(
                effect=iam.Effect.ALLOW,
                actions=[
                    'ssm:GetParameter*'
                ],
                resources=[
                    f"{parameter_arn_prefix}{self._twitter_api_config['ConsumerKeySsmParameter']}",
                    f"{parameter_arn_prefix}{self._twitter_api_config['ConsumerSecretSsmParameter']}",
                    f"{parameter_arn_prefix}{self._twitter_api_config['AccessTokenSsmParameter']}",
                    f"{parameter_arn_prefix}{self._twitter_api_config['AccessTokenSecretSsmParameter']}"
                ]
            ),
            iam.PolicyStatement(
                effect=iam.Effect.ALLOW,
                actions=[
                    'kms:Decrypt'
                ],
                resources=[
                    kms.Alias.from_alias_name(self, 'kms-key-for-ssm', 'alias/aws/ssm').key_arn
                ]
            ),
            iam.PolicyStatement(
                effect=iam.Effect.ALLOW,
                actions=[
                    'firehose:PutRecord'
                ],
                resources=[
                   self._delivery_stream.delivery_stream_arn
                ]
            ),
        ]
