import typing

from aws_cdk import core as cdk
from aws_cdk import aws_iam as iam

from ..config.environment import EnvironmentConfig
from ..constants.service_principal import ServicePrincipal
from benedict import benedict


class EcsTaskDefinition(cdk.Construct):
    def __init__(self,
                 scope: cdk.Construct,
                 id: str,
                 config: EnvironmentConfig,
                 task_name: str,
                 policy_statements: typing.Sequence[iam.PolicyStatement],
                 aws_managed_policy_names: typing.Sequence[str]):
        super().__init__(scope, id)

        self._config: EnvironmentConfig = config
        self._task_name: str = task_name
        self._policy_statements: typing.Sequence[iam.PolicyStatement] = policy_statements
        self._aws_managed_policy_names: typing.Sequence[str] = aws_managed_policy_names
        self._common_config: benedict = config.section('Common')

    def define_task_role(self) -> iam.Role:
        role: iam.Role = iam.Role(
            self,
            'task-role',
            role_name=f"{self._config.resource_prefix}-{self._task_name}-task-role",
            assumed_by=iam.ServicePrincipal(ServicePrincipal.ECS_TASK)
        )

        role.add_to_policy(iam.PolicyStatement(
            effect=iam.Effect.value,
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

        if self._common_config.get_bool('XRayEnabled'):
            role.add_managed_policy(iam.ManagedPolicy.from_aws_managed_policy_name('AWSXRayDaemonWriteAccess'))

        for name in self._aws_managed_policy_names:
            role.add_to_policy(iam.ManagedPolicy.from_aws_managed_policy_name(name))

        return role
