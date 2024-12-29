from typing import Callable

import Domain.Domain as Domain
import Programs.Test.CheckAllStructureTypes as CheckAllStructureTypes
import Programs.Test.DataminerClassesTest as DataminerClassesTest
import Programs.Test.DataminerCollectionTest as DataminerCollectionTest
import Programs.Test.DataminerSettingsTest as DataminerSettingsTest
import Programs.Test.StructureTest as StructureTest
import Programs.Test.TestUtil as TestUtil
import Utilities.UserInput as UserInput


def main(domain:Domain.Domain) -> None:
    tests:dict[str,Callable[[Domain.Domain],None]] = {
        "check_all_structure_types": CheckAllStructureTypes.check_all_structure_types,
        "dataminer_classes": TestUtil.create_test_function(DataminerClassesTest.DataminerClassPlan),
        "dataminer_collections": TestUtil.create_test_function(DataminerCollectionTest.DataminerCollectionPlan),
        "dataminer_settings": TestUtil.create_test_function(DataminerSettingsTest.DataminerSettingsPlan),
        "structures": TestUtil.create_test_function(StructureTest.StructurePlan),
    }
    UserInput.input_single(tests, "test", show_options=True, close_enough=True)(domain)
