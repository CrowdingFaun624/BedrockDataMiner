from typing import TYPE_CHECKING, Callable, Sequence, cast

import Component.Component as Component
import Component.ComponentTyping as ComponentTyping
import Component.Field.ComponentListField as ComponentListField
import Component.Field.Field as Field
import Component.Pattern as Pattern
import Component.Version.VersionFileComponent as VersionFileComponent

if TYPE_CHECKING:
    import Component.Version.VersionFileTypeComponent as VersionFileTypeComponent

VERSION_FILE_PATTERN:Pattern.Pattern[VersionFileComponent.VersionFileComponent] = Pattern.Pattern([{"is_version_file": True}])

class VersionFileListField(ComponentListField.ComponentListField[VersionFileComponent.VersionFileComponent]):

    __slots__ = ()

    def __init__(self, subcomponents_data: Sequence[ComponentTyping.VersionFileTypedDict], path: list[str | int]) -> None:
        super().__init__(subcomponents_data, VERSION_FILE_PATTERN, path, allow_inline=Field.InlinePermissions.inline, assume_type=VersionFileComponent.VersionFileComponent.class_name)

    def set_field(
        self,
        source_component:"Component.Component",
        components:dict[str,"Component.Component"],
        imported_components:dict[str,dict[str,"Component.Component"]],
        functions:dict[str,Callable],
        create_component_function:ComponentTyping.CreateComponentFunction,
    ) -> tuple[list[VersionFileComponent.VersionFileComponent],list[VersionFileComponent.VersionFileComponent]]:
        # adding the auto-assigning VersionFileTypes.
        version_file_type_components = cast(dict[str,"VersionFileTypeComponent.VersionFileTypeComponent"], imported_components["version_file_types"])
        subcomponents_data = cast(list[ComponentTyping.VersionFileTypedDict], self.subcomponents_data)
        already_version_file_types = {version_file["version_file_type"] for version_file in subcomponents_data}
        subcomponents_data.extend(
            version_file_type_component.auto_assign_dict
            for version_file_type_component in version_file_type_components.values()
            if version_file_type_component.auto_assign_dict is not None and version_file_type_component.name not in already_version_file_types
        )
        return super().set_field(source_component, components, imported_components, functions, create_component_function)
