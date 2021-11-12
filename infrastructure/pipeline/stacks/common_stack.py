from aws_cdk import core as cdk
from aws_cdk import aws_ec2 as ec2
from aws_cdk import aws_ecs as ecs
from benedict import benedict

from ..config.environment import EnvironmentConfig
from ..constructs.networking import Networking


class CommonStack(cdk.Stack):
    def __init__(self, scope: cdk.Construct, id: str, config: EnvironmentConfig, **kwargs) -> None:
        super().__init__(scope, id, **kwargs)

        self._config: EnvironmentConfig = config

        networking = Networking(self, 'networking', config.for_sections(['Vpc']))
        self.vpc: ec2.Vpc = networking.vpc

        self._define_ecs_cluster()

    def _define_ecs_cluster(self):
        ecs_cluster_config: benedict = self._config.section('EcsCluster')
        self.ecs_cluster: ecs.Cluster = ecs.Cluster(
            self,
            'ecs-cluster',
            cluster_name=f"{self._config.resource_prefix}-cluster",
            vpc=self.vpc,
            enable_fargate_capacity_providers=True,
            container_insights=ecs_cluster_config.get_bool('ContainerInsightsEnabled'))
