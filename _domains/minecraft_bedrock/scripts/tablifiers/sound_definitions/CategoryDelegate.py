from types import EllipsisType
from typing import Any

import _domains.minecraft_bedrock.scripts.tablifiers.sound_definitions.PrimitiveDelegate as PrimitiveDelegate
import Structure.SimpleContainer as SCon
import Structure.StructureEnvironment as StructureEnvironment
import Utilities.Trace as Trace

__all__ = ("CategoryDelegate",)

normal_categories = {"weather", "block", "bucket", "bottle", "ui", "player", "hostile", "music", "record", "neutral", "ambient"} # https://wiki.bedrock.dev/concepts/sounds#top-level-keys

class CategoryDelegate(PrimitiveDelegate.PrimitiveDelegate):

    def print_branch(self, data: SCon.SCon[Any], trace: Trace.Trace, environment: StructureEnvironment.PrinterEnvironment) -> str | EllipsisType:
        is_valid = data.data in normal_categories
        output = super().print_branch(data, trace, environment)
        return output if is_valid else f"– ({output})"
