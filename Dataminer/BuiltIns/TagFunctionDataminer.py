from collections import defaultdict
from typing import Any, Mapping

import Utilities.Exceptions as Exceptions
from Dataminer.AbstractDataminerCollection import AbstractDataminerCollection
from Dataminer.Dataminer import Dataminer
from Dataminer.DataminerEnvironment import DataminerEnvironment
from Structure.DataPath import DataPath
from Structure.StructureTag import StructureTag
from Utilities.TypeVerifier import (
    ListTypeVerifier,
    TypedDictKeyTypeVerifier,
    TypedDictTypeVerifier,
)


class TagFunctionDataminer(Dataminer):

    __slots__ = (
        "arguments",
        "function_name",
        "none_okay",
        "tag_names",
    )

    parameters = TypedDictTypeVerifier(
        TypedDictKeyTypeVerifier("arguments", False, dict),
        TypedDictKeyTypeVerifier("function_name", True, str),
        TypedDictKeyTypeVerifier("tag_names", True, ListTypeVerifier(str, list)),
        TypedDictKeyTypeVerifier("none_okay", False, bool),
    )

    def initialize(self, function_name:str, tag_names:list[str], arguments:dict[str,Any]={}, none_okay:bool=True) -> None:
        self.arguments:Mapping[str,Any] = arguments
        self.function_name = function_name
        self.tag_names = tag_names
        self.none_okay = none_okay

    def activate(self, environment:DataminerEnvironment) -> list[DataPath|Any]:
        function = self.domain.callables.get(self.function_name, self.domain)
        tags = [self.domain.script_referenceable.get(tag_name, StructureTag) for tag_name in self.tag_names]

        dependencies = set(self.dependencies)
        printer_environment = environment.get_printer_environment(self.version, self.settings.structure_info)
        tag_dataminer_collections:defaultdict[AbstractDataminerCollection,list[StructureTag]] = defaultdict(lambda: [])
        for tag in tags:
            for dataminer_collection in self.domain.dataminer_collections.values():
                if dataminer_collection.has_tag(tag) and dataminer_collection.supports_version(self.version):
                    if dataminer_collection not in dependencies:
                        raise Exceptions.TagSearcherDependencyError(self, tag, dataminer_collection)
                    tag_dataminer_collections[dataminer_collection].append(tag)

        mentioned_tags:defaultdict[StructureTag,set[DataPath]] = defaultdict(lambda: set())
        for dataminer_collection, tags in tag_dataminer_collections.items():
            for tag, paths in dataminer_collection.get_tag_paths_from_raw(dataminer_collection.get_data_file(self.version), self.version, tags, printer_environment).items():
                mentioned_tags[tag].update(paths)

        output = function(mentioned_tags, **self.arguments)
        if not self.none_okay and len(output) == 0:
            raise Exceptions.DataminerNothingFoundError(self)
        return output
