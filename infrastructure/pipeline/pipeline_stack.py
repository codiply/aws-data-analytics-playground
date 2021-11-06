from aws_cdk import core as cdk
from aws_cdk import aws_codepipeline as codepipeline
from aws_cdk import aws_codepipeline_actions as cpactions
from aws_cdk import pipelines

from .stages.main_stage import MainStage


class CdkPipelineStack(cdk.Stack):
    def __init__(self, scope: cdk.Construct, id: str, **kwargs) -> None:
        super().__init__(scope, id, **kwargs)

        source_artifact = codepipeline.Artifact()
        cloud_assembly_artifact = codepipeline.Artifact()

        pipeline = pipelines.CdkPipeline(
            self,
            'pipeline',
            pipeline_name='aws-data-analytics',
            cloud_assembly_artifact=cloud_assembly_artifact,
            source_action=cpactions.GitHubSourceAction(
                action_name='GitHub',
                output=source_artifact,
                oauth_token=cdk.SecretValue.secrets_manager(secret_id='/github/oauth-token'),
                owner='codiply',
                repo='aws-data-analytics-playground',
                branch='main',
                trigger=cpactions.GitHubTrigger.POLL),
            synth_action=pipelines.SimpleSynthAction(
                source_artifact=source_artifact,
                cloud_assembly_artifact=cloud_assembly_artifact,
                install_command='npm install -g aws-cdk && pip install -r requirements.txt',
                build_command='pytest unittests',
                synth_command='cdk synth'))

        pipeline.add_application_stage(MainStage(self, 'pre-stage', env={
            'account': '847334008802',
            'region': 'eu-west-1'
        }))

        pipeline.add_application_stage(MainStage(self, 'pro-stage', env={
            'account': '814312087360',
            'region': 'eu-west-1'
        }))