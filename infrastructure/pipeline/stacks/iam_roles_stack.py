from aws_cdk import core as cdk

from ..config.environment import EnvironmentConfig
from ..constructs.roles.databrew_role import DataBrewRole
from ..constructs.roles.glue_role import GlueRole


class IamRolesStack(cdk.Stack):
    def __init__(self,
                 scope: cdk.Construct,
                 id: str,
                 config: EnvironmentConfig,
                 **kwargs) -> None:
        super().__init__(scope, id, **kwargs)

        DataBrewRole(
            self,
            'databrew-role',
            config.for_sections([])
        )

        GlueRole(
            self,
            'glue-role',
            config.for_sections([])
        )
