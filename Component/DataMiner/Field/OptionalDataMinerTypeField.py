import Component.Field.Field as Field
import Component.ScriptImporter as ScriptImporter
import DataMiner.BuiltIns.AllFilesDataMiner as AllFilesDataMiner
import DataMiner.BuiltIns.GrabMultipleFilesDataMiner as GrabMultipleFilesDataMiner
import DataMiner.BuiltIns.GrabReFilesDataMiner as GrabReFilesDataMiner
import DataMiner.BuiltIns.GrabSingleFileDataMiner as GrabSingleFileDataMiner
import DataMiner.BuiltIns.TagSearcherDataMiner as TagSearcherDataMiner
import DataMiner.DataMiner as DataMiner

BUILT_IN_DATAMINER_CLASSES = {dataminer_class.__name__: dataminer_class for dataminer_class in [
    DataMiner.DataMiner,
    AllFilesDataMiner.AllFilesDataMiner,
    GrabMultipleFilesDataMiner.GrabMultipleFilesDataMiner,
    GrabReFilesDataMiner.GrabReFilesDataMiner,
    GrabSingleFileDataMiner.GrabSingleFileDataMiner,
    TagSearcherDataMiner.TagSearcherDataMiner,
]}

DATAMINER_CLASSES = ScriptImporter.import_scripted_types("dataminers/", BUILT_IN_DATAMINER_CLASSES, DataMiner.DataMiner)

class OptionalDataMinerTypeField(Field.Field):

    def __init__(self, dataminer_name:str|None, path: list[str | int]) -> None:
        '''
        :dataminer_name: The name of the DataMiner referenced by this Field.
        :path: A list of strings and/or integers that represent, in order from shallowest to deepest, the path through keys/indexes to get to this value.
        '''
        super().__init__(path)
        self.dataminer = DATAMINER_CLASSES[dataminer_name] if dataminer_name is not None else DataMiner.NullDataMiner

    def get_final(self) -> type[DataMiner.DataMiner]|type[DataMiner.NullDataMiner]:
        return self.dataminer

    def exists(self) -> bool:
        "Returns True if this Field was initialized with a str, and False if it was initialized with None"
        return self.dataminer is not DataMiner.NullDataMiner
