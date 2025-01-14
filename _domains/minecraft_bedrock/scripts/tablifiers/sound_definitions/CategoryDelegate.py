import _domains.minecraft_bedrock.scripts.tablifiers.sound_definitions.PrimitiveDelegate as PrimitiveDelegate
import Structure.StructureEnvironment as StructureEnvironment
import Structure.Trace as Trace

__all__ = ["CategoryDelegate"]

normal_categories = {"weather", "block", "bucket", "bottle", "ui", "player", "hostile", "music", "record", "neutral", "ambient"} # https://wiki.bedrock.dev/concepts/sounds#top-level-keys

class CategoryDelegate(PrimitiveDelegate.PrimitiveDelegate):

    def print_text(self, data: str, environment: StructureEnvironment.PrinterEnvironment) -> tuple[str, list[Trace.ErrorTrace]]:
        is_valid = data in normal_categories
        output, exceptions = super().print_text(data, environment)
        if not is_valid:
            output = f"– ({output})"
        return output, exceptions
