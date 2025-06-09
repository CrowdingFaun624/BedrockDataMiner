from types import EllipsisType
from typing import Any

from Structure.Delegate.Delegate import Delegate
from Structure.StructureBase import StructureBase
from Structure.StructureEnvironment import ComparisonEnvironment
from Utilities.Trace import Trace
from Utilities.TypeVerifier import TypedDictTypeVerifier

HEADER = "<!--This page was automatically generated. If you need to update it, consider notifying the author of the generator, CrowdingFaun624, instead of manually changing it.-->\n\n"

FOOTER = '''
<noinclude>
[[ja:Sounds.json/Bedrock Editionの値]]
[[pt:Sounds.json/Valores da Edição Bedrock]]
[[ru:Sounds.json/Значения в Bedrock Edition]]
[[uk:Sounds.json/Значення в Bedrock Edition]]
[[zh:Sounds.json/基岩版数据值]]
[[Category:Data pages]]
</noinclude>
'''

__all__ = ("BaseDelegate",)

class BaseDelegate(Delegate[Any, Any, StructureBase[dict[str,dict[Any,Any]], Any, str], Any, Any, str, Any]):

    __slots__ = ()
    type_verifier = TypedDictTypeVerifier()

    applies_to = (StructureBase,)

    def print_comparison(self, data: Any, bundle:tuple[int,...], trace: Trace, environment: ComparisonEnvironment) -> str | EllipsisType:
        if self.structure.structure is None:
            return HEADER + FOOTER
        comparison:str|EllipsisType = self.structure.structure.print_comparison(data, bundle, trace, environment)
        if comparison is ...:
            return ...
        comparison = HEADER + comparison + FOOTER
        return comparison
