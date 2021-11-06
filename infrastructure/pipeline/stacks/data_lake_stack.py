from aws_cdk import core as cdk
from aws_cdk import aws_s3 as s3


class DataLakeStack(cdk.Stack):
    def __init__(self, scope: cdk.Construct, id: str, **kwargs) -> None:
        super().__init__(scope, id, **kwargs)

        bucket = s3.Bucket(
            self,
            's3-bucket',
            removal_policy=cdk.RemovalPolicy.DESTROY)