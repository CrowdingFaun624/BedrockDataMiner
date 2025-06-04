from typing import Callable

import Domain.Domain as Domain
import Programs.Test.CheckAllStructureTypes as CheckAllStructureTypes
import Programs.Test.DataminerClassesTest as DataminerClassesTest
import Programs.Test.DataminerCollectionTest as DataminerCollectionTest
import Programs.Test.DataminerSettingsTest as DataminerSettingsTest
import Programs.Test.StructureTest as StructureTest
from Programs.Test.TestUtil import create_test_function
from Utilities.UserInput import input_single


def main(domain:Domain.Domain) -> None:
    tests:dict[str,Callable[[Domain.Domain],None]] = {
        "check_all_structure_types": CheckAllStructureTypes.check_all_structure_types,
        "dataminer_classes": create_test_function(DataminerClassesTest.DataminerClassPlan),
        "dataminer_collections": create_test_function(DataminerCollectionTest.DataminerCollectionPlan),
        "dataminer_settings": create_test_function(DataminerSettingsTest.DataminerSettingsPlan),
        "structures": create_test_function(StructureTest.StructurePlan),
    }
    input_single(tests, "test", show_options=True, close_enough=True)(domain)
