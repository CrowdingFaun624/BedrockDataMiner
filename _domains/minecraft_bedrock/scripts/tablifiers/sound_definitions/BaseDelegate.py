from typing import Any, Sequence

import Structure.Delegate.Delegate as Delegate
import Structure.StructureBase as StructureBase
import Structure.StructureEnvironment as StructureEnvironment
import Structure.Trace as Trace
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

class BaseDelegate(Delegate.Delegate[str,StructureBase.StructureBase,str]):

    type_verifier = TypeVerifier.TypedDictTypeVerifier()

    applies_to = (StructureBase.StructureBase,)

    def compare_text(self, data: Any, environment: StructureEnvironment.ComparisonEnvironment) -> tuple[Any, bool, Sequence[Trace.ErrorTrace]]:
        comparison, has_changes, exceptions = self.get_structure().structure.compare_text(data, environment)
        comparison += FOOTER
        return comparison, has_changes, exceptions
