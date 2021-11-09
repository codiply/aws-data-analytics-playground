#!/usr/bin/env python3
import os
import typing

from aws_cdk import core as cdk
from benedict import benedict

from pipeline.config.pipeline import PipelineConfig
from pipeline.pipeline_stack import CdkPipelineStack

app = cdk.App()

config_directory: str = os.path.join(os.path.dirname(os.path.realpath(__file__)), "config")
pipeline_name: typing.Optional[str] = app.node.try_get_context("pipeline_name")
pipeline_config: PipelineConfig = PipelineConfig(config_directory=config_directory, pipeline_name=pipeline_name)
ci_cd_config: benedict = pipeline_config.for_ci_cd_environment()


CdkPipelineStack(app,
                 f"{ci_cd_config['Project']}-ci-cd-pipeline",
                 pipeline_config,
                 env=cdk.Environment(account=ci_cd_config["AccountId"], region=ci_cd_config["Region"]))

app.synth()
