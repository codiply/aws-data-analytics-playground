from aws_cdk import core as cdk
from aws_cdk import aws_codepipeline as codepipeline
from aws_cdk import aws_codepipeline_actions as cpactions
from aws_cdk import pipelines

from .config.environment import EnvironmentConfig
from .config.pipeline import PipelineConfig
from .stages.main_stage import MainStage


class CdkPipelineStack(cdk.Stack):
    def __init__(self, scope: cdk.Construct, id: str, config: PipelineConfig, **kwargs) -> None:
        super().__init__(scope, id, **kwargs)

        source_artifact = codepipeline.Artifact()
        cloud_assembly_artifact = codepipeline.Artifact()

        source = pipelines.CodePipelineSource.git_hub(
            repo_string='codiply/aws-data-analytics-playground',
            branch='main',
            authentication=cdk.SecretValue.secrets_manager(secret_id='/github/oauth-token'))

        pipeline = pipelines.CodePipeline(
            self,
            'pipeline',
            pipeline_name='aws-data-analytics',
            cross_account_keys=True,
            self_mutation=True,
            synth=pipelines.ShellStep('Synthesize',
                                      input=source,
                                      primary_output_directory='infrastructure/cdk.out',
                                      commands=[
                                          "cd infrastructure",
                                          "npm install -g aws-cdk",
                                          "python -m pip install -r requirements.txt",
                                          "cdk synth"
                                      ]))

        environment_config: EnvironmentConfig
        for environment_config in config.for_all_environments():
            if environment_config.environment_enabled:
                pipeline.add_stage(MainStage(self,
                                             environment_config.environment_name,
                                             environment_config,
                                             env=cdk.Environment(account=environment_config.account_id,
                                                                 region=environment_config.region)))
