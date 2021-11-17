from aws_cdk import core as cdk
from aws_cdk import aws_ec2 as ec2
from aws_cdk import aws_glue as glue

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
            'relational-database',
            config.for_sections(['RelationalDatabase']),
            vpc=vpc
        )

        self.database_client_sg = relational_database.client_sg

        glue.Connection(
            self,
            'relational-database-glue-connection',
            connection_name=f"{config.resource_prefix}-relational-database",
            type=glue.ConnectionType.JDBC,
            properties={
                "JDBC_CONNECTION_URL": relational_database.jdbc_url,
                "USERNAME": relational_database.username,
                "PASSWORD": "TO BE UPDATED MANUALLY"
            },
            security_groups=[relational_database.database_sg],
            subnet=vpc.select_subnets(subnet_type=ec2.SubnetType.PRIVATE).subnets[0]
        )
