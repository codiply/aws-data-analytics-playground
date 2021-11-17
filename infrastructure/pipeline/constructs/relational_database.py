from aws_cdk import core as cdk
from aws_cdk import aws_ec2 as ec2
from aws_cdk import aws_rds as rds

from ..config.environment import EnvironmentConfig
from ..constants.ports import Ports


class RelationalDatabase(cdk.Construct):
    def __init__(self,
                 scope: cdk.Construct,
                 id: str,
                 config: EnvironmentConfig,
                 vpc: ec2.Vpc):
        super().__init__(scope, id)

        relational_database_config = config.section('RelationalDatabase')

        self.database_sg = ec2.SecurityGroup(
            self,
            'database-security-group',
            security_group_name=f"{config.resource_prefix}-database",
            vpc=vpc
        )
        self.database_sg.add_ingress_rule(
            peer=self.database_sg,
            connection=ec2.Port.all_tcp(),
            description="Allow all traffic from the security group itself"
        )

        self.client_sg = ec2.SecurityGroup(
            self,
            'database-client-security-group',
            security_group_name=f"{config.resource_prefix}-database-client",
            vpc=vpc
        )
        self.database_sg.add_ingress_rule(
            peer=self.client_sg,
            connection=ec2.Port.tcp(Ports.POSTGRES),
            description="Allow Postgres traffic from client security group"
        )

        database_name: str = relational_database_config['InitialDatabaseName']
        username: str = relational_database_config['MasterUsername']
        password_secret = cdk.SecretValue.ssm_secure(
                    parameter_name=relational_database_config['MasterPasswordSsmParameter'],
                    version='1')
        instance = rds.DatabaseInstance(
            self,
            'database',
            instance_identifier=f"{config.resource_prefix}-database",
            engine=rds.DatabaseInstanceEngine.postgres(version=rds.PostgresEngineVersion.VER_13_4),
            instance_type=ec2.InstanceType.of(
                instance_class=ec2.InstanceClass.BURSTABLE3,
                instance_size=ec2.InstanceSize.MICRO),
            vpc=vpc,
            multi_az=relational_database_config.get_bool('MultiAz'),
            credentials=rds.Credentials.from_password(
                username=username,
                password=password_secret
            ),
            database_name=database_name,
            removal_policy=cdk.RemovalPolicy.DESTROY,
            security_groups=[self.database_sg]
        )

        self.jdbc_url = cdk.Fn.join("",
                                    [
                                        "jdbc:postgresql://",
                                        instance.instance_endpoint.hostname,
                                        f":{Ports.POSTGRES}/{database_name}"
                                    ])
        self.username = username
