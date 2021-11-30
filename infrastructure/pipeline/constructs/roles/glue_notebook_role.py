from aws_cdk import core as cdk
from aws_cdk import aws_iam as iam

from .service_iam_role import ServiceIamRole
from ...config.environment import EnvironmentConfig
from ...constants.resource_arn import ResourceArn
from ...constants.service_principal import ServicePrincipal


class GlueNotebookRole(cdk.Construct):
    def __init__(self, scope: cdk.Construct, id: str, config: EnvironmentConfig):
        super().__init__(scope, id)

        policy_statements = [
            iam.PolicyStatement(
                effect=iam.Effect.ALLOW,
                actions=["s3:ListBucket"],
                resources=[f"arn:aws:s3:::aws-glue-jes-prod-{cdk.Aws.REGION}-assets"],
            ),
            iam.PolicyStatement(
                effect=iam.Effect.ALLOW,
                actions=["s3:GetObject"],
                resources=[f"arn:aws:s3:::aws-glue-jes-prod-{cdk.Aws.REGION}-assets*"],
            ),
            iam.PolicyStatement(
                effect=iam.Effect.ALLOW,
                actions=[
                    "logs:CreateLogStream",
                    "logs:DescribeLogStreams",
                    "logs:PutLogEvents",
                    "logs:CreateLogGroup",
                ],
                resources=[
                    f"arn:aws:logs:{cdk.Aws.REGION}:{cdk.Aws.ACCOUNT_ID}:log-group:/aws/sagemaker/*",
                    f"arn:aws:logs:{cdk.Aws.REGION}:{cdk.Aws.ACCOUNT_ID}:"
                    "log-group:/aws/sagemaker/*:log-stream:aws-glue-*",
                ],
            ),
            iam.PolicyStatement(
                effect=iam.Effect.ALLOW,
                actions=[
                    "glue:UpdateDevEndpoint",
                    "glue:GetDevEndpoint",
                    "glue:GetDevEndpoints",
                ],
                resources=[
                    "arn:aws:glue:{cdk.Aws.REGION}:{cdk.Aws.ACCOUNT_ID}:devEndpoint/*"
                ],
            ),
            iam.PolicyStatement(
                effect=iam.Effect.ALLOW,
                actions=["sagemaker:ListTags"],
                resources=[
                    "arn:aws:sagemaker:{cdk.Aws.REGION}:{cdk.Aws.ACCOUNT_ID}:notebook-instance/*"
                ],
            ),
            iam.PolicyStatement(
                effect=iam.Effect.ALLOW,
                actions=["s3:*"],
                resources=[
                    ResourceArn.bucket(config),
                    f"{ResourceArn.bucket(config)}/*",
                ],
            ),
        ]
        service_iam_role = ServiceIamRole(
            self,
            "service-iam-role",
            config.for_sections([]),
            role_name_prefix="AWSGlueServiceSageMakerNotebookRole-",
            short_name="",
            full_name="AWS Glue Notebook",
            service_principal=ServicePrincipal.SAGEMAKER,
            policy_statements=policy_statements,
        )

        self.role = service_iam_role.role
