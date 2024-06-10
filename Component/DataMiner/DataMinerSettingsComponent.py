from typing import TYPE_CHECKING, cast

import Component.Capabilities as Capabilities
import Component.Component as Component
import Component.ComponentTyping as ComponentTyping
import Component.DataMiner.Field.OptionalDataMinerTypeField as OptionalDataMinerTypeField
import Component.Field.ComponentField as ComponentField
import Component.Field.Field as Field
import Component.Field.FieldListField as FieldListField
import Component.Pattern as Pattern
import DataMiners.DataMiner as DataMiner
import Utilities.Exceptions as Exceptions
import Utilities.TypeVerifier.TypeVerifier as TypeVerifier

if TYPE_CHECKING:
    import Component.DataMiner.DataMinerCollectionComponent as DataMinerCollectionComponent

DEPENDENCY_PATTERN:Pattern.Pattern["DataMinerCollectionComponent.DataMinerCollectionComponent"] = Pattern.Pattern([{"is_dataminer_collection": True}])

class DataMinerSettingsComponent(Component.Component[DataMiner.DataMinerSettings]):

    class_name_article = "a DataMinerSettings"
    class_name = "DataMinerSettings"
    my_capabilities = Capabilities.Capabilities(is_dataminer_settings=True)
    type_verifier = TypeVerifier.TypedDictTypeVerifier(
        TypeVerifier.TypedDictKeyTypeVerifier("type", "a str", False, str),
        TypeVerifier.TypedDictKeyTypeVerifier("new", "a str or None", True, (str, type(None))),
        TypeVerifier.TypedDictKeyTypeVerifier("old", "a str or None", True, (str, type(None))),
        TypeVerifier.TypedDictKeyTypeVerifier("name", "a str or None", True, (str, type(None))),
        TypeVerifier.TypedDictKeyTypeVerifier("files", "a list", False, TypeVerifier.ListTypeVerifier(str, list, "a str", "a list")),
        TypeVerifier.TypedDictKeyTypeVerifier("dependencies", "a list", False, TypeVerifier.ListTypeVerifier(str, list, "a str", "a list")),
        TypeVerifier.TypedDictKeyTypeVerifier("parameters", "a dict", False, dict),
    )

    def __init__(self, data:ComponentTyping.DataMinerSettingsComponentTypedDict, name: str, component_group: str) -> None:
        super().__init__(data, name, component_group)
        self.verify_arguments(data, name)

        self.new = data["new"]
        self.old = data["old"]
        self.files = data.get("files", None)
        self.parameters = data.get("parameters", {})

        self.dataminer_field = OptionalDataMinerTypeField.OptionalDataMinerTypeField(data["name"], ["name"])
        self.dependencies_field = FieldListField.FieldListField([
            ComponentField.ComponentField(
                dependency_name,
                DEPENDENCY_PATTERN,
                ["dependencies", index],
                allow_inline=Field.InLinePermissions.reference
            ) for index, dependency_name in enumerate(data.get("dependencies", []))
        ], ["dependencies"])
        self.fields.extend([self.dataminer_field, self.dependencies_field])

    def create_final(self) -> None:
        super().create_final()
        self.final = DataMiner.DataMinerSettings(
            start_version_str=self.old,
            end_version_str=self.new,
            files=[] if self.files is None else self.files,
            kwargs=self.parameters
        )

    def link_finals(self) -> None:
        super().link_finals()
        parent = cast("DataMinerCollectionComponent.DataMinerCollectionComponent", self.get_inline_parent())
        self.get_final().link_subcomponents(
            file_name=parent.file_name,
            name=parent.name,
            structure=parent.structure_field.get_final(),
            dataminer_class=self.dataminer_field.get_final(),
            dependencies=list(self.dependencies_field.map(lambda dataminer_collection_component: dataminer_collection_component.get_component().get_final()))
        )

    def check(self) -> list[Exception]:
        exceptions = super().check()
        if self.dataminer_field.exists():
            if self.files is None:
                exceptions.append(Exceptions.DataMinerCollectionFileError(False, self, "when \"name\" is not null"))
        else:
            if self.files is not None:
                exceptions.append(Exceptions.DataMinerCollectionFileError(True, self, "when \"name\" is null"))
        dataminer_class = self.dataminer_field.get_final()
        parameters = dataminer_class.parameters
        if parameters is not None:
            type_verifier_trace = TypeVerifier.make_trace([self, dataminer_class.__name__])
            exceptions.extend(parameters.verify(self.parameters, type_verifier_trace))
        return exceptions
