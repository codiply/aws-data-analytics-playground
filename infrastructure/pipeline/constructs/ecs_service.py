import typing

from aws_cdk import core as cdk
from aws_cdk import aws_ec2 as ec2
from aws_cdk import aws_ecs as ecs
from aws_cdk import aws_iam as iam
from aws_cdk import aws_logs as logs

from .ecs_task_definition import EcsTaskDefinition


class EcsService(cdk.Construct):
    def __init__(self,
                 scope: cdk.Construct,
                 id: str,
                 ecs_cluster: ecs.Cluster,
                 resource_prefix: str,
                 service_name: str,
                 container_image_directory: str,
                 environment: dict,
                 memory_limit_mib: int,
                 cpu: int,
                 desired_count: int,
                 xray_enabled: bool = False,
                 policy_statements: typing.Sequence[iam.PolicyStatement] = [],
                 aws_managed_policy_names: typing.Sequence[str] = [],
                 security_groups: typing.Sequence[ec2.SecurityGroup] = [],
                 log_retention: logs.RetentionDays = logs.RetentionDays.THREE_DAYS,
                 fargate_base: int = 0,
                 fargate_weight_above_base: int = 1,
                 fargate_spot_base: int = 0,
                 fargate_spot_weight_above_base: int = 0):
        super().__init__(scope, id)

        extra_environment = {
            "SERVICE_NAME": service_name
        }
        merged_environment = {**extra_environment, **environment}

        task_definition = EcsTaskDefinition(
            self,
            'ecs-task-definition',
            resource_prefix=resource_prefix,
            task_name=service_name,
            container_image_directory=container_image_directory,
            environment=merged_environment,
            memory_limit_mib=memory_limit_mib,
            cpu=cpu,
            policy_statements=policy_statements,
            aws_managed_policy_names=aws_managed_policy_names,
            xray_enabled=xray_enabled
        )

        ecs.FargateService(
            self,
            'ecs-service',
            service_name=service_name,
            cluster=ecs_cluster,
            task_definition=task_definition.task_definition,
            desired_count=desired_count,
            security_groups=security_groups,
            capacity_provider_strategies=[
                ecs.CapacityProviderStrategy(
                    capacity_provider='FARGATE',
                    base=fargate_base,
                    weight=fargate_weight_above_base
                ),
                ecs.CapacityProviderStrategy(
                    capacity_provider='FARGATE_SPOT',
                    base=fargate_spot_base,
                    weight=fargate_spot_weight_above_base
                )
            ]
        )
