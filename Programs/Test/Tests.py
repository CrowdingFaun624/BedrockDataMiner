from typing import Callable

import Domain.Domain as Domain
import Programs.Test.CheckAllStructureTypes as CheckAllStructureTypes
import Programs.Test.DataMinerClassesTest as DataMinerClassesTest
import Programs.Test.DataMinerCollectionTest as DataMinerCollectionTest
import Programs.Test.DataMinerSettingsTest as DataMinerSettingsTest
import Programs.Test.StructureTest as StructureTest
import Programs.Test.TestUtil as TestUtil
import Utilities.UserInput as UserInput


def main(domain:Domain.Domain) -> None:
    tests:dict[str,Callable[[Domain.Domain],None]] = {
        "check_all_structure_types": CheckAllStructureTypes.check_all_structure_types,
        "dataminer_classes": TestUtil.create_test_function(DataMinerClassesTest.DataMinerClassPlan),
        "dataminer_collections": TestUtil.create_test_function(DataMinerCollectionTest.DataMinerCollectionPlan),
        "dataminer_settings": TestUtil.create_test_function(DataMinerSettingsTest.DataMinerSettingsPlan),
        "structures": TestUtil.create_test_function(StructureTest.StructurePlan),
    }
    UserInput.input_single(tests, "test", show_options=True, close_enough=True)(domain)
