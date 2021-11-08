from aws_cdk import core as cdk
from aws_cdk import aws_s3 as s3
from benedict import benedict

from ..config.environment import EnvironmentConfig


class DataLakeStack(cdk.Stack):
    def __init__(self, scope: cdk.Construct, id: str, config: EnvironmentConfig, **kwargs) -> None:
        super().__init__(scope, id, **kwargs)

        s3_bucket_config: benedict = config.config['S3Bucket']

        bucket = s3.Bucket(
            self,
            's3-bucket',
            removal_policy=cdk.RemovalPolicy.DESTROY,
            lifecycle_rules=[
                s3.LifecycleRule(expiration=cdk.Duration.days(s3_bucket_config['ExpirationDays']))
            ])