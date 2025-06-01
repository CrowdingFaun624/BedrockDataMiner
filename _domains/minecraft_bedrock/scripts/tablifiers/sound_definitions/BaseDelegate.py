from types import EllipsisType
from typing import Any

import Structure.Delegate.Delegate as Delegate
import Structure.StructureBase as StructureBase
import Structure.StructureEnvironment as StructureEnvironment
import Utilities.Trace as Trace
import Utilities.TypeVerifier as TypeVerifier

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

class BaseDelegate(Delegate.Delegate[Any, Any, StructureBase.StructureBase[dict[str,dict[Any,Any]], Any, str], Any, Any, str, Any]):

    type_verifier = TypeVerifier.TypedDictTypeVerifier()

    applies_to = (StructureBase.StructureBase,)

    def print_comparison(self, data: Any, trace: Trace.Trace, environment: StructureEnvironment.ComparisonEnvironment) -> str | EllipsisType:
        if self.structure.structure is None:
            return FOOTER
        comparison:str|EllipsisType = self.structure.structure.print_comparison(data, trace, environment)
        if comparison is ...:
            return ...
        comparison += FOOTER
        return comparison
