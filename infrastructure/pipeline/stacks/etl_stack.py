from aws_cdk import core as cdk
from aws_cdk import aws_glue as glue
from aws_cdk import aws_iam as iam

from ..config.environment import EnvironmentConfig
from ..constants.resource_names import ResourceNames
from ..constants.s3_paths import S3Paths


class EtlStack(cdk.Stack):
    def __init__(self,
                 scope: cdk.Construct,
                 id: str,
                 config: EnvironmentConfig,
                 glue_role: iam.Role,
                 **kwargs) -> None:
        super().__init__(scope, id, **kwargs)

        self._config: EnvironmentConfig = config
        self._etl_config = config.section('Etl')

        self.glue_database = glue.Database(
            self,
            'glue-database',
            database_name=f"{config.resource_prefix}"
        )

        glue.CfnCrawler(
            self,
            'raw-data-glue-crawler',
            name=f"{config.resource_prefix}-tweets-raw-data-crawler",
            table_prefix="tweets_",
            targets=glue.CfnCrawler.TargetsProperty(
                s3_targets=[
                    glue.CfnCrawler.S3TargetProperty(
                        path=f"s3://{ResourceNames.bucket(config)}/{config.section('Tweets')['S3PathPrefix']}/" +
                             f"{S3Paths.RAW_EVENTS}"
                    )
                ]
            ),
            role=glue_role.role_arn,
            database_name=self.glue_database.database_name,
            recrawl_policy=glue.CfnCrawler.RecrawlPolicyProperty(recrawl_behavior='CRAWL_NEW_FOLDERS_ONLY'),
            schedule=glue.CfnCrawler.ScheduleProperty(
                schedule_expression=f"cron({self._etl_config['Crawlers.TweetsRawData.ScheduleCronExpression']})")
        )
