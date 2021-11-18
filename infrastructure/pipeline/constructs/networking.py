from aws_cdk import core as cdk
from aws_cdk import aws_ec2 as ec2

from ..config.environment import EnvironmentConfig


class Networking(cdk.Construct):
    def __init__(self, scope: cdk.Construct, id: str, config: EnvironmentConfig):
        super().__init__(scope, id)

        vpc_config = config.section('Vpc')

        nat_gateway_provider: ec2.NatProvider
        if vpc_config['UseNatInstances']:
            nat_gateway_provider = ec2.NatInstanceProvider.instance(
                instance_type=ec2.InstanceType(vpc_config['NatInstanceType']))
        else:
            nat_gateway_provider = ec2.NatInstanceProvider.gateway()

        vpc = ec2.Vpc(self, 'vpc',
                      cidr=vpc_config['CidrRange'],
                      max_azs=vpc_config['MaxAzs'],
                      nat_gateway_provider=nat_gateway_provider,
                      nat_gateways=vpc_config['NatGateways'],
                      subnet_configuration=[
                          ec2.SubnetConfiguration(
                              cidr_mask=24,
                              name="public",
                              subnet_type=ec2.SubnetType.PUBLIC
                          ),
                          ec2.SubnetConfiguration(
                              cidr_mask=22,
                              name="private",
                              subnet_type=ec2.SubnetType.PRIVATE
                          )
                      ],
                      enable_dns_hostnames=True,
                      enable_dns_support=True)
        cdk.Tags.of(vpc).add('Name', f"{config.resource_prefix}-vpc")

        self.vpc = vpc

        ec2.GatewayVpcEndpoint(
            self,
            's3-vpc-endpoint',
            vpc=vpc,
            service=ec2.GatewayVpcEndpointAwsService.S3
        )

        ec2.InterfaceVpcEndpoint(
            self,
            'rds-vpc-endpoint',
            vpc=vpc,
            service=ec2.InterfaceVpcEndpointAwsService.RDS
        )
