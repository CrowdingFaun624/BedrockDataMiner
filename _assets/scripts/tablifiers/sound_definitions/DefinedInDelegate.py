import Structure.AbstractIterableStructure as AbstractIterableStructure
import Structure.Delegate.Delegate as Delegate
import Structure.Difference as D
import Structure.StructureEnvironment as StructureEnvironment
import Structure.Trace as Trace
import Utilities.TypeVerifier.TypeVerifier as TypeVerifier

__all__ = ["DefinedInDelegate"]


class DefinedInDelegate(Delegate.Delegate[str, AbstractIterableStructure.AbstractIterableStructure, str]):

    type_verifier = TypeVerifier.TypedDictTypeVerifier()

    applies_to = (AbstractIterableStructure.AbstractIterableStructure,)

    def compare_text(self, data:list[str|D.Diff[str]], environment: StructureEnvironment.ComparisonEnvironment) -> tuple[str, bool, list[Trace.ErrorTrace]]:
        output:list[str] = []
        exceptions:list[Trace.ErrorTrace] = []
        has_changes = False
        for index, item in enumerate(data):
            structure, new_exceptions = self.get_structure().get_structure(index, item)
            exceptions.extend(exception.add(self.get_structure().name, index) for exception in new_exceptions)
            assert structure is not None
            comparison, any_changes, new_exceptions = structure.compare_text(D.last_value(item), environment)
            has_changes = has_changes or any_changes
            output.append(comparison)
        return "Defined in packs %s" % (", ".join(output),), has_changes, exceptions
