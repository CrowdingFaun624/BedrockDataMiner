from typing import Any

import DataMiner.DataMinerEnvironment as DataMinerEnvironment
import DataMiner.DataMiners as DataMiners
import DataMiner.TagSearcher.TagSearcherDataMiner as TagSearcherDataMiner
import Structure.DataPath as DataPath
import Utilities.Exceptions as Exceptions
import Utilities.TypeVerifier.TypeVerifier as TypeVerifier


class TagSearcherDataMiner0(TagSearcherDataMiner.TagSearcherDataMiner):

    parameters = TypeVerifier.TypedDictTypeVerifier(
        TypeVerifier.TypedDictKeyTypeVerifier("tags", "a str", True, str),
        TypeVerifier.TypedDictKeyTypeVerifier("sort_output", "a bool", True, bool),
        TypeVerifier.TypedDictKeyTypeVerifier("none_okay", "a bool", False, bool),
    )

    def initialize(self, **kwargs) -> None:
        self.tags:str = kwargs["tags"]
        self.sort_output = kwargs["sort_output"]
        self.none_okay = kwargs.get("none_okay", False)

    def activate(self, environment:DataMinerEnvironment.DataMinerEnvironment) -> list[DataPath.DataPath|Any]:
        tag_function, tag_names = TagSearcherDataMiner.parse(self.tags)
        mentioned_tags:dict[str,set[DataPath.DataPath]] = {}
        dependencies = set(self.dependencies)
        for tag in tag_names:
            mentioned_tags[tag] = set()
            for dataminer_collection in DataMiners.dataminers:
                if dataminer_collection.has_tag(tag) and dataminer_collection not in dependencies:
                    raise Exceptions.TagSearcherDependencyError(self, tag, dataminer_collection)
                mentioned_tags[tag].update(dataminer_collection.get_tag_paths(self.version, tag, environment.structure_environment))
        output = tag_function(mentioned_tags)

        if not self.none_okay and len(output) == 0:
            raise Exceptions.DataMinerNothingFoundError(self)

        output_list = list(output)
        if self.sort_output:
            output_list.sort() # type: ignore
        return output_list
