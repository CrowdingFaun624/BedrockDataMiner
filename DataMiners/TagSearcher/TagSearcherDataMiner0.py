from typing import Any

import DataMiners.DataMiners as DataMiners
import DataMiners.DataMinerTyping as DataMinerTyping
import DataMiners.TagSearcher.TagSearcherDataMiner as TagSearcherDataMiner
import Structure.DataPath as DataPath
import Structure.Normalizer as Normalizer
import DataMiners.DataMinerParameters as DataMinerParameters

class TagSearcherDataMiner0(TagSearcherDataMiner.TagSearcherDataMiner):

    parameters = DataMinerParameters.TypedDictParameters({
        "tags": (str, True),
        "sort_output": (bool, True),
        "none_okay": (bool, False),
    })

    def initialize(self, **kwargs) -> None:
        self.tags:str = kwargs["tags"]
        self.sort_output = kwargs["sort_output"]
        # self.record_type = RecordType[kwargs["record_type"]]
        self.none_okay = kwargs.get("none_okay", False)

    def activate(self, dependency_data: DataMinerTyping.DependenciesTypedDict) -> list[DataPath.DataPath|Any]:
        normalizer_dependencies = Normalizer.NormalizerDependencies({}, DataMiners.dataminers)

        tag_function, tag_names = TagSearcherDataMiner.parse(self.tags)
        mentioned_tags:dict[str,set[DataPath.DataPath]] = {}
        dependencies = set(self.dependencies)
        for tag in tag_names:
            mentioned_tags[tag] = set()
            for dataminer_collection in DataMiners.dataminers:
                if dataminer_collection.has_tag(tag) and dataminer_collection.name not in dependencies:
                    raise RuntimeError("DataMiner %s could find tag \"%s\" in DataMiner %s, but it is not a dependency!" % (self, tag, dataminer_collection))
                mentioned_tags[tag].update(dataminer_collection.get_tag_paths(self.version, tag, normalizer_dependencies, environment.structure_environment))
        output = tag_function(mentioned_tags)

        if not self.none_okay and len(output) == 0:
            raise RuntimeError("None of the specified tags found in \"%s\"!" % (self.version))

        output_list = list(output)
        if self.sort_output:
            output_list.sort() # type: ignore
        return output_list
