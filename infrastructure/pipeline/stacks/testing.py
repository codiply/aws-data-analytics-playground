import typing

from aws_cdk import core as cdk
from aws_cdk import aws_ec2 as ec2

from ..config.environment import EnvironmentConfig
from ..constructs.test_instance import TestInstance


class TestingStack(cdk.Stack):
    def __init__(self,
                 scope: cdk.Construct,
                 id: str,
                 config: EnvironmentConfig,
                 vpc: ec2.Vpc,
                 relational_database_client_sg: typing.Optional[ec2.SecurityGroup],
                 redshift_client_sg: typing.Optional[ec2.SecurityGroup],
                 **kwargs) -> None:
        super().__init__(scope, id, **kwargs)

        TestInstance(
            self,
            'test-instance',
            config.for_sections(['Common', 'TestInstance']),
            vpc=vpc,
            relational_database_client_sg=relational_database_client_sg,
            redshift_client_sg=redshift_client_sg
        )
