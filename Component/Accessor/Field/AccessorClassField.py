import Component.Component as Component
import Component.ComponentTyping as ComponentTyping
import Component.Field.Field as Field
import Component.ScriptImporter as ScriptImporter
import Downloader.Accessor as Accessor


class AccessorClassField(Field.Field):

    __slots__ = (
        "accessor_class",
        "accessor_class_str",
    )

    def __init__(self, accessor_class_str:str, path: list[str | int]) -> None:
        '''
        :accessor_class_str: The name of the Accessor class this Field refers to.
        :path: A list of strings and/or integers that represent, in order from shallowest to deepest, the path through keys/indexes to get to this value.
        '''
        super().__init__(path)
        self.accessor_class_str = accessor_class_str
        self.accessor_class:type["Accessor.Accessor"]

    def set_field(
        self,
        source_component:Component.Component,
        components:dict[str, Component.Component],
        global_components: dict[str, dict[str, dict[str, Component.Component]]],
        functions: ScriptImporter.ScriptSetSetSet,
        create_component_function: ComponentTyping.CreateComponentFunction
    ) -> tuple[list[Component.Component], list[Component.Component]]:
        self.accessor_class = functions.accessor_classes.get(self.accessor_class_str, source_component, self.error_path)
        return [], []
