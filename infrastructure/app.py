#!/usr/bin/env python3
import os

from aws_cdk import core as cdk
from benedict import benedict

from config.pipeline import PipelineConfig
from pipeline.pipeline_stack import CdkPipelineStack

config_directory: str = os.path.join(os.path.dirname(os.path.realpath(__file__)), "config")
pipeline_config: PipelineConfig = PipelineConfig(config_directory=config_directory, pipeline_name=None)
ci_cd_config: benedict = pipeline_config.for_ci_cd_environment()

app = cdk.App()
CdkPipelineStack(app,
                 f"{ci_cd_config['Project']}-ci-cd-pipeline",
                 pipeline_config,
                 env=cdk.Environment(account=ci_cd_config["AccountId"], region=ci_cd_config["Region"]))

app.synth()
