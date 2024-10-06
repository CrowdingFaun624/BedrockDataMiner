import Programs.Test.DataMinerClassesTest as DataMinerClassesTest
import Programs.Test.DataMinerCollectionTest as DataMinerCollectionTest
import Programs.Test.DataMinerSettingsTest as DataMinerSettingsTest
import Programs.Test.StructureTest as StructureTest
import Programs.Test.TestUtil as TestUtil


def main() -> None:
    tests = {
        "dataminer_classes": TestUtil.create_test_function(DataMinerClassesTest.DataMinerClassPlan),
        "dataminer_collections": TestUtil.create_test_function(DataMinerCollectionTest.DataMinerCollectionPlan),
        "dataminer_settings": TestUtil.create_test_function(DataMinerSettingsTest.DataMinerSettingsPlan),
        "structures": TestUtil.create_test_function(StructureTest.StructurePlan),
    }
    user_input:str|None = None
    while user_input not in tests:
        user_input = input("Choose a test: [%s]\n" % (", ".join(tests.keys())))
    tests[user_input]()
