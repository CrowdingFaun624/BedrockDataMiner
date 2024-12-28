import Component.Field.Field as Field
import Utilities.TypeVerifier.TypeVerifier as TypeVerifier
import Utilities.TypeVerifier.TypeVerifierImporter as TypeVerifierImporter


class TypeVerifierField(Field.Field):

    __slots__ = (
        "type_verifier",
    )

    def __init__(self, data:TypeVerifierImporter.TypedVerifierTypedDicts, path:list[str|int]) -> None:
        '''
        :data: The data of the TypeVerifier.
        :path: A list of strings and/or integers that represent, in order from shallowest to deepest, the path through keys/indexes to get to this value.
        '''
        super().__init__(path)
        self.type_verifier = TypeVerifierImporter.parse_type_verifier(data)

    def get_final(self) -> TypeVerifier.TypeVerifier:
        return self.type_verifier
