import typing

from aws_cdk import core as cdk
from aws_cdk import aws_iam as iam

from ...config.environment import EnvironmentConfig


class ServiceIamRole(cdk.Construct):
    def __init__(self,
                 scope: cdk.Construct,
                 id: str,
                 config: EnvironmentConfig,
                 short_name: str,
                 full_name: str,
                 service_principal: str,
                 policy_statements: typing.Sequence[iam.PolicyStatement] = [],
                 aws_managed_policy_names: typing.Sequence[str] = [],
                 customer_managed_policies: typing.Sequence[iam.Policy] = []):
        super().__init__(scope, id)

        self.role: iam.Role = iam.Role(
            self,
            'iam-role',
            role_name=f"{config.resource_prefix}-{short_name}-role",
            description=f"Role for {full_name} for {config.project} in {config.environment_name}",
            assumed_by=iam.ServicePrincipal(service_principal)
        )

        for statement in policy_statements:
            self.role.add_to_policy(statement)

        for name in aws_managed_policy_names:
            self.role.add_managed_policy(iam.ManagedPolicy.from_aws_managed_policy_name(name))

        for policy in customer_managed_policies:
            policy.attach_to_role(self.role)
