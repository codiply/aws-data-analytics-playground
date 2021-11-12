from aws_cdk import core as cdk
from aws_cdk import aws_iam as iam
from aws_cdk import aws_s3 as s3

from ..config.environment import EnvironmentConfig
from ..constants.resource_names import ResourceNames
from ..constructs.roles.databrew_role import DataBrewRole
from ..constructs.roles.glue_role import GlueRole


class BaseStack(cdk.Stack):
    def __init__(self, scope: cdk.Construct, id: str, config: EnvironmentConfig, **kwargs) -> None:
        super().__init__(scope, id, **kwargs)

        self._config: EnvironmentConfig = config

        self._define_s3_bucket()
        self._define_roles()

    def _define_s3_bucket(self):
        s3_bucket_config: dict = self._config.section('S3Bucket')

        self.s3_bucket = s3.Bucket(
            self,
            's3-bucket',
            bucket_name=ResourceNames.bucket(self._config),
            removal_policy=cdk.RemovalPolicy.DESTROY,
            auto_delete_objects=True,
            lifecycle_rules=[
                s3.LifecycleRule(expiration=cdk.Duration.days(s3_bucket_config['ExpirationDays']))
            ])

    def _define_roles(self):
        self.data_brew_role: iam.Role = DataBrewRole(
            self,
            'databrew-role',
            self._config.for_sections([])
        ).role

        self.glue_role: iam.Role = GlueRole(
            self,
            'glue-role',
            self._config.for_sections([])
        ).role
