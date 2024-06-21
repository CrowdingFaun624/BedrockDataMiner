from typing import Sequence, TypeVar

import Structure.AbstractIterableStructure as AbstractIterableStructure
import Structure.Difference as D
import Structure.StructureEnvironment as StructureEnvironment
import Structure.Trace as Trace

d = TypeVar("d")

class SetStructure(AbstractIterableStructure.AbstractIterableStructure[d]):
    """
    Unordered data structure.
    """

    def compare(
        self,
        data1:Sequence[d],
        data2:Sequence[d],
        environment:StructureEnvironment.StructureEnvironment,
    ) -> tuple[Sequence[d|D.Diff[d|D.NoExist,d|D.NoExist]],bool,list[Trace.ErrorTrace]]:
        if data1 is data2 or data1 == data2:
            return data1, False, []
        has_changes = False
        exceptions:list[Trace.ErrorTrace] = []

        output:list[d|D.Diff[d|D.NoExist,d|D.NoExist]] = type(data1)() # type: ignore
        exceptions:list[Trace.ErrorTrace] = []
        for index, item in enumerate(data1):
            if (check_type_exception := self.check_type(index, item)) is not None:
                exceptions.append(check_type_exception)
            if item in data2:
                output.append(item) # item in both
            else:
                output.append(D.Diff(old=item))
                has_changes = True
        for index, item in enumerate(data2):
            if (check_type_exception := self.check_type(index, item)) is not None:
                exceptions.append(check_type_exception)
            if item in data1:
                pass # ignore; already added.
            else:
                output.append(D.Diff(new=item))
                has_changes = True
        return output, has_changes, exceptions

    def get_item_key(self, index: int) -> str:
        return ""

    def get_compare_text_key_str(self, index:int) -> str|int|None:
        return None
