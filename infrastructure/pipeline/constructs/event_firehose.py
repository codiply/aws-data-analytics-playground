from aws_cdk import core as cdk
from aws_cdk import aws_iam as iam
from aws_cdk import aws_kinesisfirehose as firehose
from aws_cdk import aws_kinesisfirehose_destinations as destinations
from aws_cdk import aws_lambda_python as lambda_python
from aws_cdk import aws_s3 as s3

from ..config.environment import EnvironmentConfig
from ..constants.resource_arn import ResourceArn
from ..constants.s3_paths import S3Paths
from ..constants.service_principal import ServicePrincipal
from benedict import benedict


class EventFirehose(cdk.Construct):
    def __init__(self,
                 scope: cdk.Construct,
                 id: str,
                 config: EnvironmentConfig,
                 s3_bucket: s3.Bucket,
                 event_name: str,
                 path_prefix: str):
        super().__init__(scope, id)

        self._config: EnvironmentConfig = config
        self._s3_bucket: s3.Bucket = s3_bucket
        self._event_name: str = event_name
        self._path_prefix: str = path_prefix

        self._event_firehose_config: benedict = config.section('EventFirehose')

        role = self._define_role()
        date_path = 'year=!{timestamp:yyyy}/month=!{timestamp:MM}/day=!{timestamp:dd}/hour=!{timestamp:HH}'

        lambda_function = lambda_python.PythonFunction(
            self,
            "processor-lambda-function",
            function_name=f"{config.resource_prefix}-{event_name}-delivery-stream-processor",
            entry="./assets/lambdas/event-firehose-processor",
            index="lambda-handler.py",
            handler="main"
        )

        lambda_processor = firehose.LambdaFunctionProcessor(lambda_function)

        self.delivery_stream: firehose.DeliveryStream = firehose.DeliveryStream(
            self,
            'firehose-delivery-stream',
            destinations=[
                destinations.S3Bucket(
                    s3_bucket,
                    processor=lambda_processor,
                    role=role,
                    buffering_interval=cdk.Duration.seconds(
                        self._event_firehose_config.get_int('BufferingIntervalSeconds')),
                    buffering_size=cdk.Size.mebibytes(
                        self._event_firehose_config.get_int('BufferingSizeMiB')),
                    data_output_prefix=f"{path_prefix}/{S3Paths.RAW_EVENTS}/{date_path}/",
                    error_output_prefix=f"{path_prefix}/{S3Paths.RAW_EVENTS_FIREHOSE_ERROR}/result=!{firehose:error-output-type}/{date_path}/",
                )
            ]
        )

        self.add_s3_lifecycle_rules()

    def _define_role(self) -> iam.Role:
        role = iam.Role(self,
                        'delivery-stram-role',
                        role_name=f"{self._config.resource_prefix}-{self._event_name}-firehose-role",
                        assumed_by=iam.ServicePrincipal(ServicePrincipal.FIREHOSE))
        role.add_to_policy(iam.PolicyStatement(
            effect=iam.Effect.ALLOW,
            actions=[
                's3:AbortMultipartUpload',
                's3:GetBucketLocation',
                's3:GetObject',
                's3:ListBucket',
                's3:ListBucketMultipartUploads',
                's3:PutObject'
            ],
            resources=[
                ResourceArn.bucket(self._config),
                f"{ResourceArn.bucket(self._config)}/{self._path_prefix}/{S3Paths.RAW_EVENTS}/*",
                f"{ResourceArn.bucket(self._config)}/{self._path_prefix}/{S3Paths.RAW_EVENTS_FIREHOSE_ERROR}/*"
            ]
        ))
        return role

    def add_s3_lifecycle_rules(self) -> None:
        self._s3_bucket.add_lifecycle_rule(
            prefix=f"{self._path_prefix}/{S3Paths.RAW_EVENTS}",
            expiration=cdk.Duration.days(self._event_firehose_config.get_int('DataOutputExpirationDays'))
        )
        self._s3_bucket.add_lifecycle_rule(
            prefix=f"{self._path_prefix}/{S3Paths.RAW_EVENTS_FIREHOSE_ERROR}",
            expiration=cdk.Duration.days(self._event_firehose_config.get_int('ErrorOutputExpirationDays'))
        )
