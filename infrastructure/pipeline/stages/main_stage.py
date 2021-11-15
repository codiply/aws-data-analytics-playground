import typing

from aws_cdk import core as cdk

from ..config.environment import EnvironmentConfig
from ..stacks.base_stack import BaseStack
from ..stacks.common_stack import CommonStack
from ..stacks.data_warehouse_stack import DataWarehouseStack
from ..stacks.etl_stack import EtlStack
from ..stacks.relational_database_stack import RelationalDatabaseStack
from ..stacks.testing import TestingStack
from ..stacks.tweets_to_s3_stack import TweetsToS3Stack


class MainStage(cdk.Stage):
    def __init__(self, scope: cdk.Construct, id: str, config: EnvironmentConfig, **kwargs):
        super().__init__(scope, id, **kwargs)

        if config.stack_enabled('Base'):
            base_stack: BaseStack = BaseStack(
                self,
                f"{config.resource_prefix}-base",
                config.for_sections(['S3Bucket'])
            )

        if config.stack_enabled('Common'):
            common_stack: CommonStack = CommonStack(
                self,
                f"{config.resource_prefix}-common",
                config.for_sections(['EcsCluster',
                                     'Vpc']))

        if config.stack_enabled('TweetsToS3'):
            TweetsToS3Stack(
                self,
                f"{config.resource_prefix}-tweets-to-s3",
                config=config.for_sections([
                    'Common',
                    'EventFirehose',
                    'Tweets',
                    'TweetsFirehoseProducer',
                    'TwitterApi']),
                s3_bucket=base_stack.s3_bucket,
                ecs_cluster=common_stack.ecs_cluster)

        data_warehouse_stack: typing.Optional[DataWarehouseStack] = None
        if config.stack_enabled('DataWarehouse'):
            data_warehouse_stack = DataWarehouseStack(
                self,
                f"{config.resource_prefix}-data-warehouse",
                config=config.for_sections(['Redshift']),
                vpc=common_stack.vpc
            )

        relational_database_stack: typing.Optional[RelationalDatabaseStack] = None
        if config.stack_enabled('RelationalDatabase'):
            relational_database_stack = RelationalDatabaseStack(
                self,
                f"{config.resource_prefix}-relational-database",
                config=config.for_sections(['RelationalDatabase']),
                vpc=common_stack.vpc
            )

        if config.stack_enabled('Etl'):
            EtlStack(
                self,
                f"{config.resource_prefix}-etl",
                config=config.for_sections(['Etl', 'Tweets']),
                glue_role=base_stack.glue_role
            )

        if config.stack_enabled('Testing'):
            TestingStack(
                self,
                f"{config.resource_prefix}-testing",
                config=config.for_sections(('Common', 'TestInstance')),
                vpc=common_stack.vpc,
                redshift_client_sg=data_warehouse_stack.redshift_client_sg if data_warehouse_stack else None,
                relational_database_client_sg=(relational_database_stack.database_client_sg
                                               if relational_database_stack else None)
            )
