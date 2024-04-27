import DataMiners.AllFiles.AllFilesDataMiner as AllFilesDataMiner
import DataMiners.DataMinerTyping as DataMinerTyping

class AllFilesDataMiner0(AllFilesDataMiner.AllFilesDataMiner):

    def activate(self, dependency_data: DataMinerTyping.DependenciesTypedDict) -> list[str]:
        return self.get_file_list()
