import enum
from typing import Any, TypeVar

import DataMiners.DataMiners as DataMiners
import DataMiners.DataMinerTyping as DataMinerTyping
import DataMiners.TagSearcher.TagSearcherDataMiner as TagSearcherDataMiner
import Structure.DataPath as DataPath
import Structure.Normalizer as Normalizer
import DataMiners.DataMinerParameters as DataMinerParameters

class RecordType(enum.Enum):
    embedded_data = "embedded_data"
    path = "path"
    both = "both"
    last_key = "last_key"

a = TypeVar("a")
def remove_duplicates(__list:list[a]) -> list[a]:
    output:list[a] = []
    already:set[a] = set()
    for item in __list:
        if item in already:
            continue
        already.add(item)
        output.append(item)
    return output

class TagSearcherDataMiner0(TagSearcherDataMiner.TagSearcherDataMiner):

    parameters = DataMinerParameters.TypedDictParameters({
        "tags": (DataMinerParameters.ListParameters(str), True),
        "not_tags": (DataMinerParameters.ListParameters(str), False),
        "sort_output": (bool, True),
        "record_type": (DataMinerParameters.LiteralParameters([record_type.value for record_type in RecordType]), True),
        "none_okay": (bool, False)
    })

    def initialize(self, **kwargs) -> None:
        self.tags:list[str] = kwargs["tags"]
        self.not_tags:list[str] = kwargs.get("not_tags", [])
        self.sort_output = kwargs["sort_output"]
        self.record_type = RecordType[kwargs["record_type"]]
        self.none_okay = kwargs.get("none_okay", False)

    def activate(self, dependency_data: DataMinerTyping.DependenciesTypedDict) -> list[DataPath.DataPath|Any]:
        normalizer_dependencies = Normalizer.NormalizerDependencies({}, DataMiners.dataminers)

        output:set[DataPath.DataPath] = set()
        not_tags:set[DataPath.DataPath] = set()
        for dataminer_collection in DataMiners.dataminers:
            for tag in self.tags:
                output.update(dataminer_collection.get_tag_paths(self.version, tag, normalizer_dependencies))
            for not_tag in self.not_tags:
                not_tags.update(dataminer_collection.get_tag_paths(self.version, not_tag, normalizer_dependencies))
        output -= not_tags

        if not self.none_okay and len(output) == 0:
            raise RuntimeError("None of the specified tags found in \"%s\"!" % (self.version))

        match self.record_type:
            case RecordType.embedded_data:
                output_list = [data_path.embedded_item for data_path in output]
            case RecordType.path:
                output_list = list(output)
                for data_path in output_list:
                    data_path.embedded_item = None
            case RecordType.both:
                output_list = list(output)
            case RecordType.last_key:
                output_list = remove_duplicates([data_path.last_key() for data_path in output])
        if self.sort_output:
            output_list.sort() # type: ignore
        return output_list
