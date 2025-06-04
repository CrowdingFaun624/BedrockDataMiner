from types import EllipsisType
from typing import Any

from _domains.minecraft_bedrock.scripts.tablifiers.sound_definitions.PrimitiveDelegate import (
    PrimitiveDelegate,
)
from Structure.SimpleContainer import SCon
from Structure.StructureEnvironment import PrinterEnvironment
from Utilities.Trace import Trace

__all__ = ("CategoryDelegate",)

normal_categories = {"weather", "block", "bucket", "bottle", "ui", "player", "hostile", "music", "record", "neutral", "ambient"} # https://wiki.bedrock.dev/concepts/sounds#top-level-keys

class CategoryDelegate(PrimitiveDelegate):

    def print_branch(self, data: SCon[Any], trace: Trace, environment: PrinterEnvironment) -> str | EllipsisType:
        is_valid = data.data in normal_categories
        output = super().print_branch(data, trace, environment)
        return output if is_valid else f"– ({output})"
