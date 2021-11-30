from aws_cdk import core as cdk
from aws_cdk import aws_ec2 as ec2
from aws_cdk import aws_redshift as redshift

from ..config.environment import EnvironmentConfig
from ..constants.ports import Ports


class RedshiftCluster(cdk.Construct):
    def __init__(
        self, scope: cdk.Construct, id: str, config: EnvironmentConfig, vpc: ec2.Vpc
    ):
        super().__init__(scope, id)

        redshift_config = config.section("Redshift")

        cluster_sg = ec2.SecurityGroup(
            self,
            "redshift-cluster-security-group",
            security_group_name=f"{config.resource_prefix}-redshift-cluster",
            vpc=vpc,
        )
        self.client_sg = ec2.SecurityGroup(
            self,
            "redshift-client-security-group",
            security_group_name=f"{config.resource_prefix}-redshift-client",
            vpc=vpc,
        )
        cluster_sg.add_ingress_rule(
            peer=self.client_sg,
            connection=ec2.Port.tcp(Ports.REDSHIFT),
            description="Allow Redshift traffic from client security group",
        )

        redshift.Cluster(
            self,
            "redshift-cluster",
            cluster_name=f"{config.resource_prefix}-cluster",
            vpc=vpc,
            master_user=redshift.Login(
                master_username=redshift_config["MasterUsername"],
                master_password=cdk.SecretValue.ssm_secure(
                    parameter_name=redshift_config["MasterPasswordSsmParameter"],
                    version="1",
                ),
            ),
            default_database_name=redshift_config["DefaultDatabaseName"],
            cluster_type=(
                redshift.ClusterType.SINGLE_NODE
                if redshift_config.get_bool("IsSingleNode")
                else redshift.ClusterType.MULTI_NODE
            ),
            number_of_nodes=(
                redshift_config.get_int("NumberOfNodes")
                if not redshift_config.get_bool("IsSingleNode")
                else None
            ),
            node_type=redshift.NodeType.DC2_LARGE,
            removal_policy=cdk.RemovalPolicy.DESTROY,
            security_groups=[cluster_sg],
        )
