import typing

from aws_cdk import core as cdk
from aws_cdk import aws_ec2 as ec2
from aws_cdk import aws_ssm as ssm

from ..config.environment import EnvironmentConfig
from ..constants.ports import Ports


class TestInstance(cdk.Construct):
    def __init__(
        self,
        scope: cdk.Construct,
        id: str,
        config: EnvironmentConfig,
        vpc: ec2.Vpc,
        relational_database_client_sg: typing.Optional[ec2.SecurityGroup],
        redshift_client_sg: typing.Optional[ec2.SecurityGroup],
    ):
        super().__init__(scope, id)

        common_config = config.section("Common")
        # test_instance_config = config.section('TestInstance')

        instance_sg = ec2.SecurityGroup(
            self,
            "test-instance-security-group",
            security_group_name=f"{config.resource_prefix}-test-instance",
            vpc=vpc,
        )

        instance_sg.add_ingress_rule(
            peer=ec2.Peer.ipv4(
                cidr_ip=ssm.StringParameter.from_string_parameter_name(
                    self,
                    "trusted-ip-range-ssm-parameter",
                    string_parameter_name=common_config["TrustedIpRangeSsmParameter"],
                ).string_value
            ),
            connection=ec2.Port.tcp(Ports.SSH),
            description="Allow SSH from trusted IP range",
        )

        ec2_instance = ec2.Instance(
            self,
            "test-instance",
            instance_name=f"{config.resource_prefix}-test-instance",
            machine_image=ec2.AmazonLinuxImage(
                generation=ec2.AmazonLinuxGeneration.AMAZON_LINUX_2
            ),
            instance_type=ec2.InstanceType.of(
                instance_class=ec2.InstanceClass.BURSTABLE3,
                instance_size=ec2.InstanceSize.MICRO,
            ),
            security_group=instance_sg,
            vpc=vpc,
            vpc_subnets=ec2.SubnetSelection(subnet_name="public"),
            key_name=common_config["KeyName"],
            user_data=self._construct_user_data(),
        )

        if relational_database_client_sg:
            ec2_instance.add_security_group(relational_database_client_sg)
        if redshift_client_sg:
            ec2_instance.add_security_group(redshift_client_sg)

    def _construct_user_data(self) -> ec2.UserData:
        user_data = ec2.UserData.for_linux()

        user_data.add_commands(
            "yum update -y", "amazon-linux-extras install -y postgresql13"
        )

        return user_data
