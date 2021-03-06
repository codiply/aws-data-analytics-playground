from aws_cdk import core as cdk
from aws_cdk import aws_ec2 as ec2

from ..config.environment import EnvironmentConfig
from ..constructs.redshift_cluster import RedshiftCluster


class DataWarehouseStack(cdk.Stack):
    def __init__(
        self,
        scope: cdk.Construct,
        id: str,
        config: EnvironmentConfig,
        vpc: ec2.Vpc,
        **kwargs
    ) -> None:
        super().__init__(scope, id, **kwargs)

        redshift_cluster = RedshiftCluster(
            self, "redshift-cluster", config.for_sections(["Redshift"]), vpc=vpc
        )

        self.redshift_client_sg = redshift_cluster.client_sg
