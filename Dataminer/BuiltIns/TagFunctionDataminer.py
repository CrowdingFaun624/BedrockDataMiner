from collections import defaultdict
from typing import Any, Sequence

import Utilities.Exceptions as Exceptions
from Component.ComponentFunctions import register_builtin
from Dataminer.AbstractDataminerCollection import AbstractDataminerCollection
from Dataminer.Dataminer import Dataminer
from Dataminer.DataminerEnvironment import DataminerEnvironment
from Structure.DataPath import DataPath
from Structure.Function import Function
from Structure.StructureTag import StructureTag
from Utilities.TypeVerifier import (
    ListTypeVerifier,
    TypedDictKeyTypeVerifier,
    TypedDictTypeVerifier,
)


@register_builtin()
class TagFunctionDataminer(Dataminer):

    __slots__ = (
        "function",
        "none_okay",
        "tags",
    )

    parameters = TypedDictTypeVerifier(
        TypedDictKeyTypeVerifier("function", True, Function),
        TypedDictKeyTypeVerifier("tags", True, ListTypeVerifier(StructureTag, list)),
        TypedDictKeyTypeVerifier("none_okay", False, bool),
    )

    def initialize(self, function:Function, tags:Sequence[StructureTag], none_okay:bool=True) -> None:
        self.function = function
        self.tags = tags
        self.none_okay = none_okay

    def activate(self, environment:DataminerEnvironment) -> list[DataPath|Any]:
        dependencies = set(self.dependencies)
        printer_environment = environment.get_printer_environment(self.version, self.settings.structure_info)
        tag_dataminer_collections:defaultdict[AbstractDataminerCollection,list[StructureTag]] = defaultdict(lambda: [])
        for tag in self.tags:
            for dataminer_collection in self.domain.dataminer_collections.values():
                if dataminer_collection.has_tag(tag) and dataminer_collection.supports_version(self.version):
                    if dataminer_collection not in dependencies:
                        raise Exceptions.TagSearcherDependencyError(self, tag, dataminer_collection)
                    tag_dataminer_collections[dataminer_collection].append(tag)

        mentioned_tags:defaultdict[StructureTag,set[DataPath]] = defaultdict(lambda: set())
        for dataminer_collection, tags in tag_dataminer_collections.items():
            for tag, paths in dataminer_collection.get_tag_paths_from_raw(dataminer_collection.get_data_file(self.version), self.version, tags, printer_environment).items():
                mentioned_tags[tag].update(paths)

        output = self.function(mentioned_tags)
        if not self.none_okay and len(output) == 0:
            raise Exceptions.DataminerNothingFoundError(self)
        return output
