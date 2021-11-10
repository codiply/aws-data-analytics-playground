import typing

from aws_cdk import core as cdk
from aws_cdk import aws_ecs as ecs
from aws_cdk import aws_iam as iam
from aws_cdk import aws_logs as logs

from ..constants.service_principal import ServicePrincipal


class EcsTaskDefinition(cdk.Construct):
    def __init__(self,
                 scope: cdk.Construct,
                 id: str,
                 resource_prefix: str,
                 task_name: str,
                 container_image_directory: str,
                 environment: dict,
                 memory_limit_mib: int,
                 cpu: int,
                 policy_statements: typing.Sequence[iam.PolicyStatement],
                 aws_managed_policy_names: typing.Sequence[str],
                 xray_enabled: bool,
                 log_retention: logs.RetentionDays = logs.RetentionDays.THREE_DAYS):
        super().__init__(scope, id)

        self._resource_prefix = resource_prefix
        self._task_name: str = task_name
        self._policy_statements: typing.Sequence[iam.PolicyStatement] = policy_statements
        self._aws_managed_policy_names: typing.Sequence[str] = aws_managed_policy_names
        self._xray_enabled: bool = xray_enabled

        xray_port = 2000

        extra_environment = {
            'AWS_XRAY_DAEMON_ADDRESS': f"127.0.0.1:{xray_port}",
            'AWS_REGION': cdk.Aws.REGION,
            'AWS_ACCOUNT_ID': cdk.Aws.ACCOUNT_ID
        }

        merged_environment = {**environment, **extra_environment}

        task_role = self.define_task_role()

        task_definition = ecs.FargateTaskDefinition(
            self,
            'task-definition',
            memory_limit_mib=memory_limit_mib,
            cpu=cpu,
            task_role=task_role
        )
        self.task_definition: ecs.FargateTaskDefinition = task_definition

        task_definition.add_container(
            'main-container',
            container_name='main-container',
            image=ecs.ContainerImage.from_asset(container_image_directory),
            environment=merged_environment,
            logging=ecs.LogDriver.aws_logs(
                stream_prefix=resource_prefix,
                log_retention=log_retention
            )
        )

        if xray_enabled:
            task_definition.add_container(
                'xray-container',
                container_name='xray-container',
                image=ecs.ContainerImage.from_registry("amazon/aws-xray-daemon:3.3.2"),
                logging=ecs.LogDriver.aws_logs(
                    stream_prefix=resource_prefix,
                    log_retention=log_retention
                ),
                command=["-o"],
                port_mappings=[
                    ecs.PortMapping(container_port=xray_port, protocol=ecs.Protocol.TCP),
                    ecs.PortMapping(container_port=xray_port, protocol=ecs.Protocol.UDP)
                ]
            )

    def define_task_role(self) -> iam.Role:
        role: iam.Role = iam.Role(
            self,
            'task-role',
            role_name=f"{self._resource_prefix}-{self._task_name}-task-role",
            assumed_by=iam.ServicePrincipal(ServicePrincipal.ECS_TASK)
        )

        role.add_to_policy(iam.PolicyStatement(
            effect=iam.Effect.ALLOW,
            actions=[
                'logs:Create*',
                'logs:PutLogEvents'
            ],
            resources=[
                'arn:aws:logs:*:*:*'
            ]
        ))

        for statement in self._policy_statements:
            role.add_to_policy(statement)

        if self._xray_enabled:
            role.add_managed_policy(iam.ManagedPolicy.from_aws_managed_policy_name('AWSXRayDaemonWriteAccess'))

        for name in self._aws_managed_policy_names:
            role.add_managed_policy(iam.ManagedPolicy.from_aws_managed_policy_name(name))

        return role
