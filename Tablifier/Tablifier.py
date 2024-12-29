from typing import Any, Callable

import Dataminer.AbstractDataminerCollection as AbstractDataminerCollection
import Structure.Difference as D
import Structure.StructureBase as StructureBase
import Structure.StructureEnvironment as StructureEnvironment
import Utilities.Exceptions as Exceptions
import Utilities.FileManager as FileManager
import Version.Version as Version
import Version.VersionProvider.VersionProvider as VersionProvider
from Utilities.File import FakeFile


class TablifierTest[a]():

    def __init__(self, data:list[Any], result:a, result_func:Callable[[Any],a]=lambda x: x) -> None:
        self.data = data
        self.result = result
        self.result_func = result_func

# all names are picked randomly from a baby name website
tests:dict[str,TablifierTest] = {
    # Test of value changes in a Keymap with Object child.
    "test1": TablifierTest(
        [
           # nnn            nnc               nn-               ncn               ncc              nc-               n-n               n-c                n--                  -nn               -nc               -n-            --n
           {"Ava": {"": 0}, "Bella": {"": 0}, "Chloe": {"": 0}, "Daisy": {"": 0}, "Emma": {"": 0}, "Fiona": {"": 0}, "Grace": {"": 0}, "Hannah": {"": 0}, "Isabella": {"": 0},                                                                   },
           {"Ava": {"": 0}, "Bella": {"": 0}, "Chloe": {"": 0}, "Daisy": {"": 1}, "Emma": {"": 1}, "Fiona": {"": 1},                                                           "Julia": {"": 0}, "Kayla": {"": 0}, "Luna": {"": 0}               },
           {"Ava": {"": 0}, "Bella": {"": 1},                   "Daisy": {"": 0}, "Emma": {"": 1},                   "Grace": {"": 0}, "Hannah": {"": 1},                      "Julia": {"": 0}, "Kayla": {"": 1},                "Mia": {"": 0} },
        ],
        {
            "Ava": {"": 0},
            "Bella": {"": D.Diff(3, {(0, 1): 0, (2,): 1})},
            D.Diff(3, {(0, 1): "Chloe"}): D.Diff(3, {(0, 1): {"": 0}}),
            "Daisy": {"": D.Diff(3, {(0,): 0, (1,): 1, (2,): 0})},
            "Emma": {"": D.Diff(3, {(0,): 0, (1,2): 1})},
            D.Diff(3, {(0, 1): "Fiona"}): D.Diff(3, {(0, 1): {"": D.Diff(3, {(0,): 0, (1,): 1})}}),
            D.Diff(3, {(0, 2): "Grace"}): D.Diff(3, {(0, 2): {"": 0}}),
            D.Diff(3, {(0, 2): "Hannah"}): D.Diff(3, {(0, 2): {"": D.Diff(3, {(0, 1): 0, (2,): 1})}}),
            D.Diff(3, {(0,): "Isabella"}): D.Diff(3, {(0,): {"": 0}}),
            D.Diff(3, {(1, 2): "Julia"}): D.Diff(3, {(1, 2): {"": 0}}),
            D.Diff(3, {(1, 2): "Kayla"}): D.Diff(3, {(1, 2): {"": D.Diff(3, {(0, 1): 0, (2,): 1})}}),
            D.Diff(3, {(1,): "Luna"}): D.Diff(3, {(1,): {"": 0}}),
            D.Diff(3, {(2,): "Mia"}): D.Diff(3, {(2,): {"": 0}}),
        },
    ),
    # Test of value changes in a Keymap with Primitive child.
    "test2": TablifierTest(
        [
            # nnn               nnc              nn-              ncn              ncc             nc-               n-n              n-c               n--                 -nn               -nc      -n-                      --n
            { "Ava": "Airport", "Bella": "Bike", "Chloe": "Case", "Daisy": "Dish", "Emma": "Exam", "Fiona": "Fight", "Grace": "Golf", "Hannah": "Hole", "Isabella": "Iron",                                                                     },
            { "Ava": "Airport", "Bella": "Bike", "Chloe": "Case", "Daisy": "Dosh", "Emma": "Emam", "Fiona": "Fhght",                                                        "Julia": "Joint", "Kayla": "Key", "Luna": "Ladder",                 },
            { "Ava": "Airport", "Bella": "Bice",                  "Daisy": "Dish", "Emma": "Emam",                   "Grace": "Golf", "Hannah": "Hale",                     "Julia": "Joint", "Kayla": "Keg",                   "Mia": "Model", },
        ],
        {
            "Ava": "Airport",
            "Bella": D.Diff(3, {(0, 1): "Bike", (2,): "Bice"}),
            D.Diff(3, {(0, 1): "Chloe"}): D.Diff(3, {(0, 1): "Case"}),
            "Daisy": D.Diff(3, {(0,): "Dish", (1,): "Dosh", (2,): "Dish"}),
            "Emma": D.Diff(3, {(0,): "Exam", (1, 2): "Emam"}),
            D.Diff(3, {(0, 1): "Fiona"}): D.Diff(3, {(0,): "Fight", (1,): "Fhght"}),
            D.Diff(3, {(0, 2): "Grace"}): D.Diff(3, {(0, 2): "Golf"}),
            D.Diff(3, {(0, 2): "Hannah"}): D.Diff(3, {(0,): "Hole", (2,): "Hale"}), # this is desired behavior. If it had an Object child, it would be combined.
            D.Diff(3, {(0,): "Isabella"}): D.Diff(3, {(0,): "Iron"}),
            D.Diff(3, {(1, 2): "Julia"}): D.Diff(3, {(1, 2): "Joint"}),
            D.Diff(3, {(1, 2): "Kayla"}): D.Diff(3, {(1,): "Key", (2,): "Keg"}),
            D.Diff(3, {(1,): "Luna"}): D.Diff(3, {(1,): "Ladder"}),
            D.Diff(3, {(2,): "Mia"}): D.Diff(3, {(2,): "Model"}),
        },
    ),
    # Test of key changes in a Dict.
    "test3": TablifierTest(
        [
            # nnn       nnc         nn-         ncn         ncc        nc-         n-n         n-c          n--            -nn         -nc         -n-         --n
            { "Ava": 0, "Bella": 1, "Chloe": 2, "Daisy": 3, "Emma": 4, "Fiona": 5, "Grace": 6, "Hannah": 7, "Isabella": 8,                                                 },
            { "Ava": 0, "Bella": 1, "Chloe": 2, "Daist": 3, "Emmm": 4, "Fionl": 5,                                         "Julia": 9, "Kayla": 10, "Luna": 11,            },
            { "Ava": 0, "Bello": 1,             "Daisy": 3, "Emmm": 4,             "Grace": 6, "Hannoh": 7,                "Julia": 9, "Kayli": 10,             "Mia": 12, },
        ],
        {
            "Ava": 0,
            D.Diff(3, {(0, 1): "Bella", (2,): "Bello"}): 1,
            D.Diff(3, {(0, 1): "Chloe"}): D.Diff(3, {(0, 1): 2}),
            D.Diff(3, {(0,): "Daisy", (1,): "Daist", (2,): "Daisy"}): 3,
            D.Diff(3, {(0,): "Emma", (1, 2): "Emmm"}): 4,
            D.Diff(3, {(0,): "Fiona", (1,): "Fionl"}): D.Diff(3, {(0, 1): 5}),
            D.Diff(3, {(0, 2): "Grace"}): D.Diff(3, {(0, 2): 6}),
            D.Diff(3, {(0,): "Hannah", (2,): "Hannoh"}): D.Diff(3, {(0, 2): 7}),
            D.Diff(3, {(0,): "Isabella"}): D.Diff(3, {(0,): 8}),
            D.Diff(3, {(1, 2): "Julia"}): D.Diff(3, {(1, 2): 9}),
            D.Diff(3, {(1,): "Kayla", (2,): "Kayli"}): D.Diff(3, {(1, 2): 10}),
            D.Diff(3, {(1,): "Luna"}): D.Diff(3, {(1,): 11}),
            D.Diff(3, {(2,): "Mia"}): D.Diff(3, {(2,): 12}),
        },
    ),
    # Test of changes in a Set with Primitive child.
    "test4": TablifierTest(
        [
            # nnn    nnc      nn-      ncn      ncc     nc-      n-n      n-c       n--         -nn      -nc     -n-     --n
            [ "Ava", "Bella", "Chloe", "Daisy", "Emma", "Fiona", "Grace", "Hannah", "Isabella",                                  ],
            [ "Ava", "Bella", "Chloe", "Daist", "Emmm", "Fionl",                                "Julia", "Kayla", "Luna",        ],
            [ "Ava", "Bello",          "Daisy", "Emmm",          "Grace", "Hannoh",             "Julia", "Kayli",         "Mia", ],
        ],
        [
            "Ava",
            D.Diff(3, {(0, 1): "Bella", (2,): "Bello"}),
            D.Diff(3, {(0, 1): "Chloe"}),
            D.Diff(3, {(0,): "Daisy", (1,): "Daist", (2,): "Daisy"}),
            D.Diff(3, {(0,): "Emma", (1,2): "Emmm"}),
            D.Diff(3, {(0,): "Fiona", (1,): "Fionl"}),
            D.Diff(3, {(0, 2): "Grace"}),
            D.Diff(3, {(0,): "Hannah", (2,): "Hannoh"}),
            D.Diff(3, {(0,): "Isabella"}),
            D.Diff(3, {(1,2): "Julia"}),
            D.Diff(3, {(1,): "Kayla", (2,): "Kayli"}),
            D.Diff(3, {(1,): "Luna"}),
            D.Diff(3, {(2,): "Mia"}),
        ],
    ),
    # Test of changes in a Set with Object child.
    "test5": TablifierTest(
        [
            # nnn                nnc                  nn-                  ncn                  ncc                 nc-                  n-n                  n-c                   n--                     -nn                  -nc                  -n-                 --n
            [ {"n":"Ava","v":0}, {"n":"Bella","v":0}, {"n":"Chloe","v":0}, {"n":"Daisy","v":0}, {"n":"Emma","v":0}, {"n":"Fiona","v":0}, {"n":"Grace","v":0}, {"n":"Hannah","v":0}, {"n":"Isabella","v":0},                                                                                  ],
            [ {"n":"Ava","v":0}, {"n":"Bella","v":0}, {"n":"Chloe","v":0}, {"n":"Daisy","v":1}, {"n":"Emma","v":1}, {"n":"Fiona","v":1},                                                                    {"n":"Julia","v":0}, {"n":"Kayla","v":0}, {"n":"Luna","v":0},                    ],
            [ {"n":"Ava","v":0}, {"n":"Bella","v":1},                      {"n":"Daisy","v":0}, {"n":"Emma","v":1},                      {"n":"Grace","v":0}, {"n":"Hannah","v":1},                         {"n":"Julia","v":0}, {"n":"Kayla","v":1},                     {"n":"Mia","v":0}, ],
        ],
        [
            {"n": "Ava", "v": 0},
            {"n": "Bella", "v": D.Diff(3, {(0, 1): 0, (2,): 1})},
            D.Diff(3, {(0, 1): {"n": "Chloe", "v": 0}}),
            {"n": "Daisy", "v": D.Diff(3, {(0,): 0, (1,): 1, (2,): 0})},
            {"n": "Emma", "v": D.Diff(3, {(0,): 0, (1, 2): 1})},
            D.Diff(3, {(0, 1): {"n": "Fiona", "v": D.Diff(3, {(0,): 0, (1,): 1})}}),
            D.Diff(3, {(0, 2): {"n": "Grace", "v": 0}}),
            D.Diff(3, {(0, 2): {"n": "Hannah", "v": D.Diff(3, {(0, 1): 0, (2,): 1})}}),
            D.Diff(3, {(0,): {"n": "Isabella", "v": 0}}),
            D.Diff(3, {(1, 2): {"n": "Julia", "v": 0}}),
            D.Diff(3, {(1, 2): {"n": "Kayla", "v": D.Diff(3, {(0, 1): 0, (2,): 1})}}),
            D.Diff(3, {(1,): {"n": "Luna", "v": 0}}),
            D.Diff(3, {(2,): {"n": "Mia", "v": 0}})
        ],
        lambda x: sorted(x, key=lambda k: D.last_value(k)["n"]),
    ),
    # Test of changes in a List
    "test6": TablifierTest(
        [
            {"a": [0,1,2], "b": [0,   ], "c": [0,1,2], "d": [0,1,2], "e": [ ], "f": [0], "g": [{"":0},{"":1},{"":2}], "h": [{"":0},             ], "i": [{"":0},{"":1},{"":2}], "j": [{"":0},{"":1},{"":2}], "k": [      ], "l": [{"":0}]},
            {"a": [0,1,2], "b": [0,1, ], "c": [0,1],   "d": [1,1,3], "e": [0], "f": [1], "g": [{"":0},{"":1},{"":2}], "h": [{"":0},{"":1},      ], "i": [{"":0},{"":1},      ], "j": [{"":1},{"":1},{"":3}], "k": [{"":0}], "l": [{"":1}]},
            {"a": [0,1,2], "b": [0,1,2], "c": [0,],    "d": [2,3,3], "e": [1], "f": [ ], "g": [{"":0},{"":1},{"":2}], "h": [{"":0},{"":1},{"":2}], "i": [{"":0},             ], "j": [{"":2},{"":3},{"":3}], "k": [{"":1}], "l": [      ]},
        ],
        {
            "a": [0,1,2],
            "b": [0, D.Diff(3, {(1,2): 1}), D.Diff(3, {(2,): 2})],
            "c": [0, D.Diff(3, {(0,1): 1}), D.Diff(3, {(0,): 2})],
            "d": [D.Diff(3, {(0,): 0, (1,): 1, (2,): 2}), D.Diff(3, {(0, 1): 1, (2,): 3}), D.Diff(3, {(0,): 2, (1, 2): 3})],
            "e": [D.Diff(3, {(1,): 0, (2,): 1})],
            "f": [D.Diff(3, {(0,): 0, (1,): 1})],
            "g": [{"":0}, {"":1}, {"":2}],
            "h": [{"":0}, D.Diff(3, {(1, 2): {"":1}}), D.Diff(3, {(2,): {"":2}})],
            "i": [{"":0}, D.Diff(3, {(0, 1): {"":1}}), D.Diff(3, {(0,): {"":2}})],
            "j": [{"":D.Diff(3, {(0,): 0, (1,): 1, (2,): 2})}, {"":D.Diff(3, {(0, 1): 1, (2,): 3})}, {"":D.Diff(3, {(0,): 2, (1, 2): 3})}],
            "k": [D.Diff(3, {(1, 2): {"":D.Diff(3, {(0, 1): 0, (2,): 1})}})],
            "l": [D.Diff(3, {(0, 1): {"":D.Diff(3, {(0,): 0, (1,): 1})}})],
        },
    ),
    # Test of changes in a Sequence
    "test7": TablifierTest(
        [ #        nnn   ncn             ncc   nnc             nn-   -nn             nc-   -nc             n-n   n-c             n--           -n-           --n
            {"a": ["Ava","Bella"], "b": ["Ava","Bella"], "c": ["Ava",       ], "d": ["Ava",       ], "e": ["Ava","Bella"], "f": ["Ava"], "g": [     ], "h": [     ]},
            {"a": ["Ava","Bello"], "b": ["Aba","Bella"], "c": ["Ava","Bella"], "d": ["Aba","Bella"], "e": [             ], "f": [     ], "g": ["Ava"], "h": [     ]},
            {"a": ["Ava","Bella"], "b": ["Aba","Bello"], "c": [      "Bella"], "d": [      "Bello"], "e": ["Ava","Bello"], "f": [     ], "g": [     ], "h": ["Ava"]},
        ],
        {
            "a": ["Ava", D.Diff(3, {(0,): "Bella", (1,): "Bello", (2,): "Bella"})],
            "b": [D.Diff(3, {(0,): "Ava", (1, 2): "Aba"}), D.Diff(3, {(0, 1): "Bella", (2,): "Bello"})],
            "c": [D.Diff(3, {(0, 1): "Ava"}), D.Diff(3, {(1, 2): "Bella"})],
            "d": [D.Diff(3, {(0,): "Ava", (1,): "Aba"}), D.Diff(3, {(1,): "Bella", (2,): "Bello"})],
            "e": [D.Diff(3, {(0, 2): "Ava"}), D.Diff(3, {(0,): "Bella", (2,): "Bello"})],
            "f": [D.Diff(3, {(0,): "Ava"})],
            "g": [D.Diff(3, {(1,): "Ava"})],
            "h": [D.Diff(3, {(2,): "Ava"})],
        },
    ),
    # Test of changes in a Group
    "test8": TablifierTest(
        [
            {"a": 0, "b": 0, "c": 0, "d": 0, "e": "Egg", "f": 0,     "g": "Egg", "h": "Egg", "i": {"": "Egg"}, "j": "Egg",       "k": {"": "Egg"}, "l": {"": "Egg"}},
            {"a": 0, "b": 1, "c": 1, "d": 0, "e": "Egg", "f": "Egg", "g": 0,     "h": "Egg", "i": {"": "Egh"}, "j": {"": "Egg"}, "k": "Egg",       "l": {"": "Egg"}},
            {"a": 0, "b": 2, "c": 1, "d": 2, "e": "Egg", "f": "Egg", "g": "Egg", "h": 0,     "i": {"": "Egi"}, "j": {"": "Egh"}, "k": {"": "Egg"}, "l": "Egg",     },
        ],
        {
            "a": 0,
            "b": D.Diff(3, {(0,): 0, (1,): 1, (2,): 2}),
            "c": D.Diff(3, {(0,): 0, (1, 2): 1}),
            "d": D.Diff(3, {(0, 1): 0, (2,): 2}),
            "e": "Egg",
            "f": D.Diff(3, {(0,): 0, (1, 2): "Egg"}),
            "g": D.Diff(3, {(0,): "Egg", (1,): 0, (2,): "Egg"}),
            "h": D.Diff(3, {(0, 1): "Egg", (2,): 0}),
            "i": {"": D.Diff(3, {(0,): "Egg", (1,): "Egh", (2,): "Egi"})},
            "j": D.Diff(3, {(0,): "Egg", (1, 2): {"": D.Diff(3, {(0, 1): "Egg", (2,): "Egh"})}}),
            "k": D.Diff(3, {(0,): {"": "Egg"}, (1,): "Egg", (2,): {"": "Egg"}}),
            "l": D.Diff(3, {(0, 1): {"": "Egg"}, (2,): "Egg"}),
        },
    ),
    # Test of changes in a File
    "test9": TablifierTest(
        # this test assumes that if the hash of a file changes, its data also changes.
        [
            {"a": FakeFile("a", 0, 0), "b": FakeFile("b", 0, 0), "c": FakeFile("c", 0, 0), "d": FakeFile("d", 0, 0), "e": FakeFile("e", {"":0}, 0), "f": FakeFile("f", {"":0}, 0), "g": FakeFile("g", {"":0}, 0), "h": FakeFile("g", {"":0}, 0)},
            {"a": FakeFile("a", 0, 0), "b": FakeFile("b", 0, 0), "c": FakeFile("c", 1, 1), "d": FakeFile("d", 1, 1), "e": FakeFile("e", {"":0}, 0), "f": FakeFile("f", {"":0}, 0), "g": FakeFile("g", {"":1}, 1), "h": FakeFile("g", {"":1}, 1)},
            {"a": FakeFile("a", 0, 0), "b": FakeFile("b", 1, 1), "c": FakeFile("c", 1, 1), "d": FakeFile("d", 0, 0), "e": FakeFile("e", {"":0}, 0), "f": FakeFile("f", {"":1}, 1), "g": FakeFile("g", {"":1}, 1), "h": FakeFile("g", {"":0}, 0)},
        ],
        {
            "a": 0,
            "b": D.Diff(3, {(0, 1): 0, (2,): 1}),
            "c": D.Diff(3, {(0,): 0, (1, 2): 1}),
            "d": D.Diff(3, {(0,): 0, (1,): 1, (2,): 0}),
            "e": {"":0},
            "f": {"":D.Diff(3, {(0, 1): 0, (2,): 1})},
            "g": {"":D.Diff(3, {(0,): 0, (1, 2): 1})},
            "h": {"":D.Diff(3, {(0,): 0, (1,): 1, (2,): 0})},
        },
        lambda data: {key: value.data for key, value in data.items()}
    ),
}

class Tablifier():

    def __init__(self, name:str, file_name:str) -> None:
        self.name = name
        self.file_name = file_name
        self.path = FileManager.OUTPUT_DIRECTORY.joinpath(self.file_name)

        self.structure:StructureBase.StructureBase|None = None
        self.dataminer_collection:AbstractDataminerCollection.AbstractDataminerCollection|None = None
        self.version_provider:VersionProvider.VersionProvider|None = None

    def link_finals(
        self,
        structure:StructureBase.StructureBase,
        dataminer_collection:AbstractDataminerCollection.AbstractDataminerCollection,
        version_provider:VersionProvider.VersionProvider,
    ) -> None:
        self.structure = structure
        self.dataminer_collection = dataminer_collection
        self.version_provider = version_provider

    def _get_versions_between(self, all_versions:list[Version.Version], versions:list[Version.Version]) -> list[list[Version.Version]]:
        version_index = 0
        between_versions:list[Version.Version] = []
        output:list[list[Version.Version]] = []
        for version in all_versions:
            if version is versions[version_index]:
                output.append(between_versions)
                version_index += 1
                if version_index >= len(versions):
                    break
                continue
            else:
                between_versions.append(version)
        return output

    def tablify(self, all_versions:list[Version.Version]) -> None:
        if self.version_provider is None:
            raise Exceptions.AttributeNoneError("version_provider", self)
        if self.dataminer_collection is None:
            raise Exceptions.AttributeNoneError("dataminer_collection", self)
        if self.structure is None:
            raise Exceptions.AttributeNoneError("structure", self)
        versions = self.version_provider.get_versions(all_versions, supports_dataminer_collection=self.dataminer_collection)
        structure_environment = StructureEnvironment.StructureEnvironment(StructureEnvironment.EnvironmentType.comparing)
        between_versions = self._get_versions_between(all_versions, versions)
        comparison_environment = StructureEnvironment.ComparisonEnvironment(structure_environment, None, versions, between_versions, True)
        if self.name in tests:
            test = tests[self.name]
            data_files = test.data
        else:
            test = None
            data_files = [self.structure.normalize(self.dataminer_collection.get_data_file(version), comparison_environment[branch]) for branch, version in enumerate(versions)]
        comparison, _ = self.structure.compare_many(*data_files, environment=comparison_environment)
        if test is not None:
            comparison = test.result_func(comparison)
        if test is not None and test.result is not None:
            if test.result != comparison:
                print(test.result)
                print("Test failed!")
            else:
                print("Test passed.")
        if test is None:
            output, _ = self.structure.compare_text(comparison, comparison_environment)
            with open(self.path, "wt", encoding="UTF8") as f:
                f.write(output)
