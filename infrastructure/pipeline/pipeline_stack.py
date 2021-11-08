from aws_cdk import core as cdk
from aws_cdk import aws_codepipeline as codepipeline
from aws_cdk import aws_codepipeline_actions as cpactions
from aws_cdk import aws_iam as iam
from aws_cdk import pipelines

from .config.environment import EnvironmentConfig
from .config.pipeline import PipelineConfig
from .stages.main_stage import MainStage


class CdkPipelineStack(cdk.Stack):
    def __init__(self, scope: cdk.Construct, id: str, config: PipelineConfig, **kwargs) -> None:
        super().__init__(scope, id, **kwargs)

        ci_cd_config: benedict = config.for_ci_cd_environment()

        source_artifact = codepipeline.Artifact()
        cloud_assembly_artifact = codepipeline.Artifact()

        source = pipelines.CodePipelineSource.git_hub(
            repo_string=ci_cd_config['GitHubRepo'],
            branch=ci_cd_config['GitBranch'],
            authentication=cdk.SecretValue.secrets_manager(secret_id=ci_cd_config['GitHubOauthTokenSsmParameter']))

        pipeline = pipelines.CodePipeline(
            self,
            'pipeline',
            pipeline_name=f"{ci_cd_config['Project']}-ci-cd-pipeline",
            cross_account_keys=True,
            self_mutation=True,
            synth=pipelines.CodeBuildStep('Synthesize',
                                          input=source,
                                          primary_output_directory='infrastructure/cdk.out',
                                          commands=[
                                              "cd infrastructure",
                                              "npm install -g aws-cdk",
                                              "python -m pip install -r requirements.txt",
                                              f"cdk synth -c pipeline_name={config.pipeline_name}"
                                          ],
                                          role_policy_statements=[
                                              iam.PolicyStatement(
                                                  actions=['sts:AssumeRole'],
                                                  resources=['*'],
                                                  conditions={
                                                      'StringEquals': {
                                                          'iam:ResourceTag/aws-cdk:bootstrap-role': 'lookup'
                                                      }
                                                  }
                                              )
                                          ]))

        environment_config: EnvironmentConfig
        for environment_config in config.for_all_environments():
            if environment_config.environment_enabled:
                pipeline.add_stage(MainStage(self,
                                             environment_config.environment_name,
                                             environment_config,
                                             env=cdk.Environment(account=environment_config.account_id,
                                                                 region=environment_config.region)))
