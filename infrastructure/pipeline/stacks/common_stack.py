from aws_cdk import core as cdk
from aws_cdk import aws_ec2 as ec2
from aws_cdk import aws_ecs as ecs
from aws_cdk import aws_s3 as s3
from benedict import benedict

from ..config.environment import EnvironmentConfig
from ..constants.resource_arn import ResourceArn
from ..constructs.networking import Networking


class CommonStack(cdk.Stack):
    def __init__(self, scope: cdk.Construct, id: str, config: EnvironmentConfig, **kwargs) -> None:
        super().__init__(scope, id, **kwargs)

        self._config: EnvironmentConfig = config

        self._define_s3_bucket()

        networking = Networking(self, 'networking', config.for_sections(['Vpc']))
        self.vpc: ec2.Vpc = networking.vpc

        self._define_ecs_cluster()

    def _define_s3_bucket(self):
        s3_bucket_config: dict = self._config.section('S3Bucket')

        self.s3_bucket = s3.Bucket(
            self,
            's3-bucket',
            bucket_name=ResourceArn.bucket(self._config),
            removal_policy=cdk.RemovalPolicy.DESTROY,
            lifecycle_rules=[
                s3.LifecycleRule(expiration=cdk.Duration.days(s3_bucket_config['ExpirationDays']))
            ])

    def _define_ecs_cluster(self):
        ecs_cluster_config: benedict = self._config.section('EcsCluster')
        self.ecs_cluster: ecs.Cluster = ecs.Cluster(
            self,
            'ecs-cluster',
            cluster_name=f"{self._config.resource_prefix}-cluster",
            vpc=self.vpc,
            enable_fargate_capacity_providers=True,
            container_insights=ecs_cluster_config.get_bool('ContainerInsightsEnabled'))
