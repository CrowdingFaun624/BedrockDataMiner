import Structure.Importer.Field.ComponentListField as ComponentListField
import Structure.Importer.NormalizerComponent as NormalizerComponent
import Structure.Importer.Pattern as Capabilities
import Structure.Normalizer as Normalizer

NORMALIZER_REQUEST_PROPERTIES:Capabilities.Pattern[NormalizerComponent.NormalizerComponent] = Capabilities.Pattern([{"is_normalizer": True}])

class NormalizerListField(ComponentListField.ComponentListField[NormalizerComponent.NormalizerComponent]):

    def __init__(self, subcomponents_strs:list[str]|str, path:list[str|int]) -> None:
        '''
        :subcomponents_strs: The names of the Components this Field refers to.
        :path: A list of strings and/or integers that represent, in order from shallowest to deepest, the path through keys/indexes to get to this value.
        '''
        super().__init__(subcomponents_strs, NORMALIZER_REQUEST_PROPERTIES, path)

    def get_finals(self) -> list[Normalizer.Normalizer]:
        '''
        Returns the Normalizers that corresponds to this Field's NormalizerComponents..
        Can only be called after `set_field`.
        '''
        output:list[Normalizer.Normalizer] = []
        for component in self.get_components():
            assert component.final is not None
            output.append(component.final)
        return output
