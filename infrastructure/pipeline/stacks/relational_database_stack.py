from aws_cdk import core as cdk
from aws_cdk import aws_ec2 as ec2

from ..config.environment import EnvironmentConfig
from ..constructs.relational_database import RelationalDatabase


class RelationalDatabaseStack(cdk.Stack):
    def __init__(self,
                 scope: cdk.Construct,
                 id: str,
                 config: EnvironmentConfig,
                 vpc: ec2.Vpc,
                 **kwargs) -> None:
        super().__init__(scope, id, **kwargs)

        relational_database = RelationalDatabase(
            self,
            'redshift-cluster',
            config.for_sections(['Redshift']),
            vpc=vpc
        )

        self.database_client_sg = relational_database.client_sg
