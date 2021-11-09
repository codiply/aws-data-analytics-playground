from aws_cdk import core as cdk
from aws_cdk import aws_s3 as s3
from benedict import benedict

from ..config.environment import EnvironmentConfig
from ..constructs.networking import Networking


class CommonStack(cdk.Stack):
    def __init__(self, scope: cdk.Construct, id: str, config: EnvironmentConfig, **kwargs) -> None:
        super().__init__(scope, id, **kwargs)

        self._config: EnvironmentConfig = config

        self._define_s3_bucket()

        # networking = Networking(self, 'networking', config.for_sections(['Vpc']))
        #
        # self.vpc = networking.vpc

    def _define_s3_bucket(self):
        s3_bucket_config: benedict = self._config.section('S3Bucket')

        self.bucket = s3.Bucket(
            self,
            's3-bucket',
            bucket_name=f"{self._config.resource_prefix}-{self._config.account_id}",
            removal_policy=cdk.RemovalPolicy.DESTROY,
            lifecycle_rules=[
                s3.LifecycleRule(expiration=cdk.Duration.days(s3_bucket_config['ExpirationDays']))
            ])
