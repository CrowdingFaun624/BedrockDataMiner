from typing import Sequence

import Component.ComponentTyping as ComponentTyping
import Component.Field.ComponentListField as ComponentListField
import Component.Field.Field as Field
import Component.Pattern as Pattern
import Component.Structure.NormalizerComponent as NormalizerComponent
import Structure.Normalizer as Normalizer

NORMALIZER_PATTERN:Pattern.Pattern[NormalizerComponent.NormalizerComponent] = Pattern.Pattern("is_normalizer")

class NormalizerListField(ComponentListField.ComponentListField[NormalizerComponent.NormalizerComponent]):

    __slots__ = (
        "_finals",
    )

    def __init__(self, subcomponents_data:Sequence[str|ComponentTyping.NormalizerTypedDict]|str|ComponentTyping.NormalizerTypedDict, path:list[str|int], *, allow_inline:Field.InlinePermissions=Field.InlinePermissions.mixed) -> None:
        '''
        :subcomponents_data: The names of the reference Components and/or the data of the inline Components this Field refers to.
        :path: A list of strings and/or integers that represent, in order from shallowest to deepest, the path through keys/indexes to get to this value.
        :allow_inline: An InlinePermissions object describing the type of subcomponent_data allowed.
        '''
        super().__init__(subcomponents_data, NORMALIZER_PATTERN, path, allow_inline=allow_inline, assume_type=NormalizerComponent.NormalizerComponent.class_name)
        self._finals:list[Normalizer.Normalizer]|None = None

    @property
    def finals(self) -> list[Normalizer.Normalizer]:
        '''
        Returns the Normalizers that corresponds to this Field's NormalizerComponents..
        Can only be called after `set_field`.
        '''
        if self._finals is None:
            self._finals = [component.final for component in self.subcomponents]
        return self._finals
