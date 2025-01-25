import Component.Component as Component
import Component.Field.ComponentField as ComponentField
import Component.Field.FieldContainer as FieldContainer
import Component.Version.VersionComponent as VersionComponent
import Utilities.Exceptions as Exceptions
import Version.VersionRange as VersionRange


class VersionRangeField(FieldContainer.FieldContainer[ComponentField.OptionalComponentField]):

    __slots__ = (
        "_final",
        "equals",
        "start_version_field",
        "stop_version_field",
    )

    def __init__(self, start_version_str:str|None, stop_version_str:str|None, path: tuple[str,...]) -> None:
        '''
        :start_version_str: The name of the oldest Version (inclusive).
        :stop_version_str: The name of the newest Version (exclusive).
        :path: A list of strings and/or integers that represent, in order from shallowest to deepest, the path through keys/indexes to get to this value.
        '''
        self.start_version_field = ComponentField.OptionalComponentField(start_version_str, VersionComponent.VERSION_PATTERN, path, assume_component_group="versions")
        self.stop_version_field = ComponentField.OptionalComponentField(stop_version_str, VersionComponent.VERSION_PATTERN, path, assume_component_group="versions")
        self.equals = start_version_str == stop_version_str
        self._final:VersionRange.VersionRange|None = None
        super().__init__([self.start_version_field, self.stop_version_field], path)

    def __contains__(self, version:"VersionComponent.VersionComponent") -> bool:
        start = self.start_version_field.subcomponent
        stop = self.stop_version_field.subcomponent
        if self.equals:
            return version == start
        elif start is None and stop is None:
            return True
        elif start is None and stop is not None:
            return version.get_index() < stop.get_index()
        elif start is not None and stop is None:
            return version.get_index() >= start.get_index()
        elif start is not None and stop is not None:
            return version.get_index() < stop.get_index() and version.get_index() >= start.get_index()
        else:
            raise Exceptions.InvalidStateError("logic has failed us")

    def check(self, source_component: Component.Component) -> list[Exception]:
        exceptions = super().check(source_component)
        start_version = self.start_version_field.subcomponent
        stop_version = self.stop_version_field.subcomponent
        if start_version is not None and stop_version is not None and start_version.get_index() > stop_version.get_index():
            exceptions.append(Exceptions.VersionRangeOrderError(self, start_version, stop_version))
        return exceptions

    def __repr__(self) -> str:
        return f"<{self.__class__.__name__} \"{str(self.start_version_field.subcomponent_data)}\"–\"{str(self.stop_version_field.subcomponent_data)}\">"

    @property
    def final(self) -> VersionRange.VersionRange:
        if self._final is None:
            self._final = VersionRange.VersionRange(self.start_version_field.map(lambda subcomponent: subcomponent.final), self.stop_version_field.map(lambda subcomponent: subcomponent.final))
        return self._final
