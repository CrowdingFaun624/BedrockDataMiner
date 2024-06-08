from typing import Sequence

import Structure.Importer.ComponentTyping as ComponentTyping
import Structure.Importer.Field.ComponentListField as ComponentListField
import Structure.Importer.Field.Field as Field
import Structure.Importer.NormalizerComponent as NormalizerComponent
import Structure.Importer.Pattern as Pattern
import Structure.Normalizer as Normalizer

NORMALIZER_REQUEST_PROPERTIES:Pattern.Pattern[NormalizerComponent.NormalizerComponent] = Pattern.Pattern([{"is_normalizer": True}])

class NormalizerListField(ComponentListField.ComponentListField[NormalizerComponent.NormalizerComponent]):

    def __init__(self, subcomponents_data:Sequence[str|ComponentTyping.NormalizerTypedDict]|str|ComponentTyping.NormalizerTypedDict, path:list[str|int], *, allow_in_line:Field.InLinePermissions=Field.InLinePermissions.mixed) -> None:
        '''
        :subcomponents_data: The names of the reference Components and/or the data of the in-line Components this Field refers to.
        :path: A list of strings and/or integers that represent, in order from shallowest to deepest, the path through keys/indexes to get to this value.
        :allow_in_line: An InLinePermissions object describing the type of subcomponent_data allowed.
        '''
        super().__init__(subcomponents_data, NORMALIZER_REQUEST_PROPERTIES, path, allow_in_line=allow_in_line)

    def get_finals(self) -> list[Normalizer.Normalizer]:
        '''
        Returns the Normalizers that corresponds to this Field's NormalizerComponents..
        Can only be called after `set_field`.
        '''
        return [component.get_final() for component in self.get_components()]
