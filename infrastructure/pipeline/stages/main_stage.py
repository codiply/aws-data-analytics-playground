from aws_cdk import core as cdk

from ..stacks.data_lake_stack import DataLakeStack

class MainStage(cdk.Stage):
    def __init__(self, scope: cdk.Construct, id: str, **kwargs):
        super().__init__(scope, id, **kwargs)

        DataLakeStack(self, 'data-lake-stack')