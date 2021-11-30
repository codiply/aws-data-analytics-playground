from aws_cdk import core as cdk
from aws_cdk import aws_iam as iam

from .service_iam_role import ServiceIamRole
from ...config.environment import EnvironmentConfig
from ...constants.resource_arn import ResourceArn
from ...constants.service_principal import ServicePrincipal


class GlueRole(cdk.Construct):
    def __init__(self, scope: cdk.Construct, id: str, config: EnvironmentConfig):
        super().__init__(scope, id)

        policy_statements = [
            iam.PolicyStatement(
                effect=iam.Effect.ALLOW,
                actions=["s3:*"],
                resources=[
                    ResourceArn.bucket(config),
                    f"{ResourceArn.bucket(config)}/*",
                ],
            )
        ]

        service_iam_role = ServiceIamRole(
            self,
            "service-iam-role",
            config.for_sections([]),
            short_name="glue",
            full_name="AWS Glue",
            service_principal=ServicePrincipal.GLUE,
            policy_statements=policy_statements,
            aws_managed_policy_names=["service-role/AWSGlueServiceRole"],
        )

        self.role = service_iam_role.role
