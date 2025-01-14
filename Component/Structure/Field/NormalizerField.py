import Component.ComponentTyping as ComponentTyping
import Component.Field.ComponentField as ComponentField
import Component.Field.Field as Field
import Component.Pattern as Pattern
import Component.Structure.NormalizerComponent as NormalizerComponent
import Structure.Normalizer as Normalizer

NORMALIZER_PATTERN:Pattern.Pattern[NormalizerComponent.NormalizerComponent] = Pattern.Pattern("is_normalizer")

class NormalizerField(ComponentField.ComponentField[NormalizerComponent.NormalizerComponent]):

    def __init__(self, subcomponent_data:str|ComponentTyping.NormalizerTypedDict, path:list[str|int], *, allow_inline:Field.InlinePermissions=Field.InlinePermissions.mixed) -> None:
        '''
        :subcomponents_data: The name of the reference Component and/or the data of the inline Component this Field refers to.
        :path: A list of strings and/or integers that represent, in order from shallowest to deepest, the path through keys/indexes to get to this value.
        :allow_inline: An InlinePermissions object describing the type of subcomponent_data allowed.
        '''
        super().__init__(subcomponent_data, NORMALIZER_PATTERN, path, allow_inline=allow_inline, assume_type=NormalizerComponent.NormalizerComponent.class_name)

    @property
    def final(self) -> Normalizer.Normalizer:
        return self.subcomponent.final
