from collections import defaultdict

from Component.ComponentFunctions import component_function
from Structure.DataPath import DataPath
from Structure.StructureTag import StructureTag


@component_function(no_arguments=True)
def tag_function(data:dict[StructureTag,set[DataPath[str,str]]]) -> dict[str,dict[str,str]]:
    data_paths = next(iter(data.values()))
    assert len(data) == 1
    output:dict[str,dict[str,str]] = defaultdict(lambda: {})
    for data_path in data_paths:
        if not data_path[-1].startswith("desc."): continue
        output[data_path[-2]][data_path[-1]] = data_path.get_embedded_data()
    # sort all data.
    output = {key1: {key2: value2 for key2, value2 in sorted(value1.items(), key=lambda item: item[0])} for key1, value1 in sorted(output.items(), key=lambda item: item[0])}
    return output
