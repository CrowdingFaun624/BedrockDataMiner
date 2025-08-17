from functools import cache
from itertools import repeat
from types import EllipsisType
from typing import Any, Callable, Sequence

import Domain.Domain as Domain
from Component.ComponentObject import ComponentObject
from Dataminer.AbstractDataminerCollection import AbstractDataminerCollection
from Structure.Difference import Diff
from Structure.IterableContainer import IDon, icon_from_list, idon_from_list
from Structure.SimpleContainer import SCon, sdon_from_bundles
from Structure.StructureBase import StructureBase
from Structure.StructureEnvironment import (
    ComparisonEnvironment,
    EnvironmentType,
    StructureEnvironment,
)
from Utilities.Exceptions import TablifierError
from Utilities.FileManager import OUTPUT_DIRECTORY
from Utilities.Trace import Trace
from Version.Version import Version
from Version.VersionProvider.VersionProvider import VersionProviderCreator


class TablifierTest[a]():

    __slots__ = (
        "data",
        "result",
        "result_func",
    )

    def __init__(self, data:list[Any], result:a, result_func:Callable[[Any],a]=lambda x: x) -> None:
        self.data = data
        self.result = result
        self.result_func = result_func

def get_test_1(domain:"Domain.Domain") -> TablifierTest:
    empty = SCon("", domain)
    false = icon_from_list(((empty, SCon(0, domain)),), {empty: SCon(0, domain)})
    true  = icon_from_list(((empty, SCon(1, domain)),), {empty: SCon(1, domain)})
    def idon(bundles:dict[tuple[int,...],bool]) -> IDon:
        diff = Diff({bundle: (false, true)[value].as_don(bundle) for bundle, value in bundles.items()}, False)
        return idon_from_list((diff for bundle in bundles.keys() for branch in bundle), {branch: (false, true)[value] for bundle, value in bundles.items() for branch in bundle})
    name:Callable[[str], SCon[str]] = lambda name: SCon(name, domain)
    input1 = {name("Ava"): false, name("Bella"): false, name("Chloe"): false, name("Daisy"): false, name("Emma"): false, name("Fiona"): false, name("Grace"): false, name("Hannah"): false, name("Isabella"): false,                                                                                    }
    input2 = {name("Ava"): false, name("Bella"): false, name("Chloe"): false, name("Daisy"): true , name("Emma"): true , name("Fiona"): true ,                                                                       name("Julia"): false, name("Kayla"): false, name("Luna"): false,                   }
    input3 = {name("Ava"): false, name("Bella"): true ,                       name("Daisy"): false, name("Emma"): true ,                       name("Grace"): false, name("Hannah"): true ,                          name("Julia"): false, name("Kayla"): true ,                      name("Mia"): false}
    input1_container = icon_from_list(input1.items(), input1)
    input2_container = icon_from_list(input2.items(), input2)
    input3_container = icon_from_list(input3.items(), input3)
    output = Diff({(0, 1, 2): idon_from_list([
        (Diff({(0, 1, 2): sdon_from_bundles({(0, 1, 2): "Ava"}, domain)}, False), Diff({(0, 1, 2): idon({(0, 1, 2): False})}, False)),
        (Diff({(0, 1, 2): sdon_from_bundles({(0, 1, 2): "Bella"}, domain)}, False), Diff({(0, 1, 2): idon({(0, 1): False, (2,): True})}, True)),
        (Diff({(0, 1, 2): sdon_from_bundles({(0, 1, 2): "Chloe"}, domain)}, False), Diff({(0, 1, 2): idon({(0, 1): False})}, True)),
        (Diff({(0, 1, 2): sdon_from_bundles({(0, 1, 2): "Daisy"}, domain)}, False), Diff({(0, 1, 2): idon({(0,): False, (1,): True, (2,): False})}, True)),
        (Diff({(0, 1, 2): sdon_from_bundles({(0, 1, 2): "Emma"}, domain)}, False), Diff({(0, 1, 2): idon({(0,): False, (1, 2): True})}, True)),
        (Diff({(0, 1): sdon_from_bundles({(0, 1): "Fiona"}, domain)}, False), Diff({(0, 1, 2): idon({(0,): False, (1,): True})}, True)),
        (Diff({(0, 2): sdon_from_bundles({(0, 2): "Grace"}, domain)}, False), Diff({(0, 1, 2): idon({(0, 2): False})}, False)),
        (Diff({(0, 2): sdon_from_bundles({(0, 2): "Hannah"}, domain)}, False), Diff({(0, 1, 2): idon({(0,): False, (2,): True})}, True)),
        (Diff({(0,): sdon_from_bundles({(0,): "Isabella"}, domain)}, False), Diff({(0, 1, 2): idon({(0,): False})}, True)),
        (Diff({(1, 2): sdon_from_bundles({(1, 2): "Julia"}, domain)}, False), Diff({(0, 1, 2): idon({(1, 2): False})}, True)),
        (Diff({(1, 2): sdon_from_bundles({(1, 2): "Kayla"}, domain)}, False), Diff({(0, 1, 2): idon({(1,): False, (2,): True})}, True)),
        (Diff({(1,): sdon_from_bundles({(1,): "Luna"}, domain)}, False), Diff({(0, 1, 2): idon({(1,): False})}, True)),
        (Diff({(2,): sdon_from_bundles({(2,): "Mia"}, domain)}, False), Diff({(0, 1, 2): idon({(2,): False})}, True)),
    ], {0: input1_container, 1: input2_container, 2: input3_container})}, True)
    return TablifierTest([input1_container, input2_container, input3_container], output)

@cache
def get_tests(domain:"Domain.Domain") -> dict[str,TablifierTest]:
    # all names are picked randomly from a baby name website
    return {
        # Test of value changes in a Keymap with Object child.
        # "test1": get_test_1(domain)
        # # Test of value changes in a Keymap with Primitive child.
        # "test2": TablifierTest(
        #     [
        #         # nnn               nnc              nn-              ncn              ncc             nc-               n-n              n-c               n--                 -nn               -nc      -n-                      --n
        #         { "Ava": "Airport", "Bella": "Bike", "Chloe": "Case", "Daisy": "Dish", "Emma": "Exam", "Fiona": "Fight", "Grace": "Golf", "Hannah": "Hole", "Isabella": "Iron",                                                                     },
        #         { "Ava": "Airport", "Bella": "Bike", "Chloe": "Case", "Daisy": "Dosh", "Emma": "Emam", "Fiona": "Fhght",                                                        "Julia": "Joint", "Kayla": "Key", "Luna": "Ladder",                 },
        #         { "Ava": "Airport", "Bella": "Bice",                  "Daisy": "Dish", "Emma": "Emam",                   "Grace": "Golf", "Hannah": "Hale",                     "Julia": "Joint", "Kayla": "Keg",                   "Mia": "Model", },
        #     ],
        #     {
        #         "Ava": "Airport",
        #         "Bella": Diff(3, {(0, 1): "Bike", (2,): "Bice"}),
        #         Diff(3, {(0, 1): "Chloe"}): Diff(3, {(0, 1): "Case"}),
        #         "Daisy": Diff(3, {(0,): "Dish", (1,): "Dosh", (2,): "Dish"}),
        #         "Emma": Diff(3, {(0,): "Exam", (1, 2): "Emam"}),
        #         Diff(3, {(0, 1): "Fiona"}): Diff(3, {(0,): "Fight", (1,): "Fhght"}),
        #         Diff(3, {(0, 2): "Grace"}): Diff(3, {(0, 2): "Golf"}),
        #         Diff(3, {(0, 2): "Hannah"}): Diff(3, {(0,): "Hole", (2,): "Hale"}), # this is desired behavior. If it had an Object child, it would be combined.
        #         Diff(3, {(0,): "Isabella"}): Diff(3, {(0,): "Iron"}),
        #         Diff(3, {(1, 2): "Julia"}): Diff(3, {(1, 2): "Joint"}),
        #         Diff(3, {(1, 2): "Kayla"}): Diff(3, {(1,): "Key", (2,): "Keg"}),
        #         Diff(3, {(1,): "Luna"}): Diff(3, {(1,): "Ladder"}),
        #         Diff(3, {(2,): "Mia"}): Diff(3, {(2,): "Model"}),
        #     },
        # ),
        # # Test of key changes in a Dict.
        # "test3": TablifierTest(
        #     [
        #         # nnn       nnc         nn-         ncn         ncc        nc-         n-n         n-c          n--            -nn         -nc         -n-         --n
        #         { "Ava": 0, "Bella": 1, "Chloe": 2, "Daisy": 3, "Emma": 4, "Fiona": 5, "Grace": 6, "Hannah": 7, "Isabella": 8,                                                 },
        #         { "Ava": 0, "Bella": 1, "Chloe": 2, "Daist": 3, "Emmm": 4, "Fionl": 5,                                         "Julia": 9, "Kayla": 10, "Luna": 11,            },
        #         { "Ava": 0, "Bello": 1,             "Daisy": 3, "Emmm": 4,             "Grace": 6, "Hannoh": 7,                "Julia": 9, "Kayli": 10,             "Mia": 12, },
        #     ],
        #     {
        #         "Ava": 0,
        #         Diff(3, {(0, 1): "Bella", (2,): "Bello"}): 1,
        #         Diff(3, {(0, 1): "Chloe"}): Diff(3, {(0, 1): 2}),
        #         Diff(3, {(0,): "Daisy", (1,): "Daist", (2,): "Daisy"}): 3,
        #         Diff(3, {(0,): "Emma", (1, 2): "Emmm"}): 4,
        #         Diff(3, {(0,): "Fiona", (1,): "Fionl"}): Diff(3, {(0, 1): 5}),
        #         Diff(3, {(0, 2): "Grace"}): Diff(3, {(0, 2): 6}),
        #         Diff(3, {(0,): "Hannah", (2,): "Hannoh"}): Diff(3, {(0, 2): 7}),
        #         Diff(3, {(0,): "Isabella"}): Diff(3, {(0,): 8}),
        #         Diff(3, {(1, 2): "Julia"}): Diff(3, {(1, 2): 9}),
        #         Diff(3, {(1,): "Kayla", (2,): "Kayli"}): Diff(3, {(1, 2): 10}),
        #         Diff(3, {(1,): "Luna"}): Diff(3, {(1,): 11}),
        #         Diff(3, {(2,): "Mia"}): Diff(3, {(2,): 12}),
        #     },
        # ),
        # # Test of changes in a Set with Primitive child.
        # "test4": TablifierTest(
        #     [
        #         # nnn    nnc      nn-      ncn      ncc     nc-      n-n      n-c       n--         -nn      -nc     -n-     --n
        #         [ "Ava", "Bella", "Chloe", "Daisy", "Emma", "Fiona", "Grace", "Hannah", "Isabella",                                  ],
        #         [ "Ava", "Bella", "Chloe", "Daist", "Emmm", "Fionl",                                "Julia", "Kayla", "Luna",        ],
        #         [ "Ava", "Bello",          "Daisy", "Emmm",          "Grace", "Hannoh",             "Julia", "Kayli",         "Mia", ],
        #     ],
        #     [
        #         "Ava",
        #         Diff(3, {(0, 1): "Bella", (2,): "Bello"}),
        #         Diff(3, {(0, 1): "Chloe"}),
        #         Diff(3, {(0,): "Daisy", (1,): "Daist", (2,): "Daisy"}),
        #         Diff(3, {(0,): "Emma", (1,2): "Emmm"}),
        #         Diff(3, {(0,): "Fiona", (1,): "Fionl"}),
        #         Diff(3, {(0, 2): "Grace"}),
        #         Diff(3, {(0,): "Hannah", (2,): "Hannoh"}),
        #         Diff(3, {(0,): "Isabella"}),
        #         Diff(3, {(1,2): "Julia"}),
        #         Diff(3, {(1,): "Kayla", (2,): "Kayli"}),
        #         Diff(3, {(1,): "Luna"}),
        #         Diff(3, {(2,): "Mia"}),
        #     ],
        # ),
        # # Test of changes in a Set with Object child.
        # "test5": TablifierTest(
        #     [
        #         # nnn                nnc                  nn-                  ncn                  ncc                 nc-                  n-n                  n-c                   n--                     -nn                  -nc                  -n-                 --n
        #         [ {"n":"Ava","v":0}, {"n":"Bella","v":0}, {"n":"Chloe","v":0}, {"n":"Daisy","v":0}, {"n":"Emma","v":0}, {"n":"Fiona","v":0}, {"n":"Grace","v":0}, {"n":"Hannah","v":0}, {"n":"Isabella","v":0},                                                                                  ],
        #         [ {"n":"Ava","v":0}, {"n":"Bella","v":0}, {"n":"Chloe","v":0}, {"n":"Daisy","v":1}, {"n":"Emma","v":1}, {"n":"Fiona","v":1},                                                                    {"n":"Julia","v":0}, {"n":"Kayla","v":0}, {"n":"Luna","v":0},                    ],
        #         [ {"n":"Ava","v":0}, {"n":"Bella","v":1},                      {"n":"Daisy","v":0}, {"n":"Emma","v":1},                      {"n":"Grace","v":0}, {"n":"Hannah","v":1},                         {"n":"Julia","v":0}, {"n":"Kayla","v":1},                     {"n":"Mia","v":0}, ],
        #     ],
        #     [
        #         {"n": "Ava", "v": 0},
        #         {"n": "Bella", "v": Diff(3, {(0, 1): 0, (2,): 1})},
        #         Diff(3, {(0, 1): {"n": "Chloe", "v": 0}}),
        #         {"n": "Daisy", "v": Diff(3, {(0,): 0, (1,): 1, (2,): 0})},
        #         {"n": "Emma", "v": Diff(3, {(0,): 0, (1, 2): 1})},
        #         Diff(3, {(0, 1): {"n": "Fiona", "v": Diff(3, {(0,): 0, (1,): 1})}}),
        #         Diff(3, {(0, 2): {"n": "Grace", "v": 0}}),
        #         Diff(3, {(0, 2): {"n": "Hannah", "v": Diff(3, {(0, 1): 0, (2,): 1})}}),
        #         Diff(3, {(0,): {"n": "Isabella", "v": 0}}),
        #         Diff(3, {(1, 2): {"n": "Julia", "v": 0}}),
        #         Diff(3, {(1, 2): {"n": "Kayla", "v": Diff(3, {(0, 1): 0, (2,): 1})}}),
        #         Diff(3, {(1,): {"n": "Luna", "v": 0}}),
        #         Diff(3, {(2,): {"n": "Mia", "v": 0}})
        #     ],
        #     lambda x: sorted(x, key=lambda k: D.last_value(k)["n"]),
        # ),
        # # Test of changes in a List
        # "test6": TablifierTest(
        #     [
        #         {"a": [0,1,2], "b": [0,   ], "c": [0,1,2], "d": [0,1,2], "e": [ ], "f": [0], "g": [{"":0},{"":1},{"":2}], "h": [{"":0},             ], "i": [{"":0},{"":1},{"":2}], "j": [{"":0},{"":1},{"":2}], "k": [      ], "l": [{"":0}]},
        #         {"a": [0,1,2], "b": [0,1, ], "c": [0,1],   "d": [1,1,3], "e": [0], "f": [1], "g": [{"":0},{"":1},{"":2}], "h": [{"":0},{"":1},      ], "i": [{"":0},{"":1},      ], "j": [{"":1},{"":1},{"":3}], "k": [{"":0}], "l": [{"":1}]},
        #         {"a": [0,1,2], "b": [0,1,2], "c": [0,],    "d": [2,3,3], "e": [1], "f": [ ], "g": [{"":0},{"":1},{"":2}], "h": [{"":0},{"":1},{"":2}], "i": [{"":0},             ], "j": [{"":2},{"":3},{"":3}], "k": [{"":1}], "l": [      ]},
        #     ],
        #     {
        #         "a": [0,1,2],
        #         "b": [0, Diff(3, {(1,2): 1}), Diff(3, {(2,): 2})],
        #         "c": [0, Diff(3, {(0,1): 1}), Diff(3, {(0,): 2})],
        #         "d": [Diff(3, {(0,): 0, (1,): 1, (2,): 2}), Diff(3, {(0, 1): 1, (2,): 3}), Diff(3, {(0,): 2, (1, 2): 3})],
        #         "e": [Diff(3, {(1,): 0, (2,): 1})],
        #         "f": [Diff(3, {(0,): 0, (1,): 1})],
        #         "g": [{"":0}, {"":1}, {"":2}],
        #         "h": [{"":0}, Diff(3, {(1, 2): {"":1}}), Diff(3, {(2,): {"":2}})],
        #         "i": [{"":0}, Diff(3, {(0, 1): {"":1}}), Diff(3, {(0,): {"":2}})],
        #         "j": [{"":Diff(3, {(0,): 0, (1,): 1, (2,): 2})}, {"":Diff(3, {(0, 1): 1, (2,): 3})}, {"":Diff(3, {(0,): 2, (1, 2): 3})}],
        #         "k": [Diff(3, {(1, 2): {"":Diff(3, {(0, 1): 0, (2,): 1})}})],
        #         "l": [Diff(3, {(0, 1): {"":Diff(3, {(0,): 0, (1,): 1})}})],
        #     },
        # ),
        # # Test of changes in a Sequence
        # "test7": TablifierTest(
        #     [ #        nnn   ncn             ncc   nnc             nn-   -nn             nc-   -nc             n-n   n-c             n--           -n-           --n
        #         {"a": ["Ava","Bella"], "b": ["Ava","Bella"], "c": ["Ava",       ], "d": ["Ava",       ], "e": ["Ava","Bella"], "f": ["Ava"], "g": [     ], "h": [     ]},
        #         {"a": ["Ava","Bello"], "b": ["Aba","Bella"], "c": ["Ava","Bella"], "d": ["Aba","Bella"], "e": [             ], "f": [     ], "g": ["Ava"], "h": [     ]},
        #         {"a": ["Ava","Bella"], "b": ["Aba","Bello"], "c": [      "Bella"], "d": [      "Bello"], "e": ["Ava","Bello"], "f": [     ], "g": [     ], "h": ["Ava"]},
        #     ],
        #     {
        #         "a": ["Ava", Diff(3, {(0,): "Bella", (1,): "Bello", (2,): "Bella"})],
        #         "b": [Diff(3, {(0,): "Ava", (1, 2): "Aba"}), Diff(3, {(0, 1): "Bella", (2,): "Bello"})],
        #         "c": [Diff(3, {(0, 1): "Ava"}), Diff(3, {(1, 2): "Bella"})],
        #         "d": [Diff(3, {(0,): "Ava", (1,): "Aba"}), Diff(3, {(1,): "Bella", (2,): "Bello"})],
        #         "e": [Diff(3, {(0, 2): "Ava"}), Diff(3, {(0,): "Bella", (2,): "Bello"})],
        #         "f": [Diff(3, {(0,): "Ava"})],
        #         "g": [Diff(3, {(1,): "Ava"})],
        #         "h": [Diff(3, {(2,): "Ava"})],
        #     },
        # ),
        # # Test of changes in a Group
        # "test8": TablifierTest(
        #     [
        #         {"a": 0, "b": 0, "c": 0, "d": 0, "e": "Egg", "f": 0,     "g": "Egg", "h": "Egg", "i": {"": "Egg"}, "j": "Egg",       "k": {"": "Egg"}, "l": {"": "Egg"}},
        #         {"a": 0, "b": 1, "c": 1, "d": 0, "e": "Egg", "f": "Egg", "g": 0,     "h": "Egg", "i": {"": "Egh"}, "j": {"": "Egg"}, "k": "Egg",       "l": {"": "Egg"}},
        #         {"a": 0, "b": 2, "c": 1, "d": 2, "e": "Egg", "f": "Egg", "g": "Egg", "h": 0,     "i": {"": "Egi"}, "j": {"": "Egh"}, "k": {"": "Egg"}, "l": "Egg",     },
        #     ],
        #     {
        #         "a": 0,
        #         "b": Diff(3, {(0,): 0, (1,): 1, (2,): 2}),
        #         "c": Diff(3, {(0,): 0, (1, 2): 1}),
        #         "d": Diff(3, {(0, 1): 0, (2,): 2}),
        #         "e": "Egg",
        #         "f": Diff(3, {(0,): 0, (1, 2): "Egg"}),
        #         "g": Diff(3, {(0,): "Egg", (1,): 0, (2,): "Egg"}),
        #         "h": Diff(3, {(0, 1): "Egg", (2,): 0}),
        #         "i": {"": Diff(3, {(0,): "Egg", (1,): "Egh", (2,): "Egi"})},
        #         "j": Diff(3, {(0,): "Egg", (1, 2): {"": Diff(3, {(0, 1): "Egg", (2,): "Egh"})}}),
        #         "k": Diff(3, {(0,): {"": "Egg"}, (1,): "Egg", (2,): {"": "Egg"}}),
        #         "l": Diff(3, {(0, 1): {"": "Egg"}, (2,): "Egg"}),
        #     },
        # ),
        # # Test of changes in a File
        # "test9": TablifierTest(
        #     # this test assumes that if the hash of a file changes, its data also changes.
        #     [
        #         {"a":FakeFile("a",0,None,0),"b":FakeFile("b",0,None,0),"c":FakeFile("c",0,None,0),"d":FakeFile("d",0,None,0),"e":FakeFile("e",{"":0},None,0),"f":FakeFile("f",{"":0},None,0),"g":FakeFile("g",{"":0},None,0),"h":FakeFile("h",{"":0},None,0)},
        #         {"a":FakeFile("a",0,None,0),"b":FakeFile("b",0,None,0),"c":FakeFile("c",1,None,1),"d":FakeFile("d",1,None,1),"e":FakeFile("e",{"":0},None,0),"f":FakeFile("f",{"":0},None,0),"g":FakeFile("g",{"":1},None,1),"h":FakeFile("h",{"":1},None,1)},
        #         {"a":FakeFile("a",0,None,0),"b":FakeFile("b",1,None,1),"c":FakeFile("c",1,None,1),"d":FakeFile("d",0,None,0),"e":FakeFile("e",{"":0},None,0),"f":FakeFile("f",{"":1},None,1),"g":FakeFile("g",{"":1},None,1),"h":FakeFile("h",{"":0},None,0)},
        #     ],
        #     {
        #         "a": 0,
        #         "b": Diff(3, {(0, 1): 0, (2,): 1}),
        #         "c": Diff(3, {(0,): 0, (1, 2): 1}),
        #         "d": Diff(3, {(0,): 0, (1,): 1, (2,): 0}),
        #         "e": {"":0},
        #         "f": {"":Diff(3, {(0, 1): 0, (2,): 1})},
        #         "g": {"":Diff(3, {(0,): 0, (1, 2): 1})},
        #         "h": {"":Diff(3, {(0,): 0, (1,): 1, (2,): 0})},
        #     },
        #     lambda data: {key: (value.data if isinstance(value, FileDiff) else value.read(None)) for key, value in data.items()}
        # ),
    }

class Tablifier(ComponentObject):

    __slots__ = (
        "dataminer_collection",
        "file_name",
        "path",
        "structure",
        "version_provider",
    )

    def link_tablifier(
        self,
        dataminer_collection:AbstractDataminerCollection,
        file_name:str,
        structure:StructureBase,
        version_provider:VersionProviderCreator,
    ) -> None:
        self.dataminer_collection = dataminer_collection
        self.file_name = file_name
        self.path = OUTPUT_DIRECTORY.joinpath(self.file_name)
        self.structure = structure
        self.version_provider = version_provider

    def _get_versions_between(self, all_versions:list[Version], versions:list[Version]) -> list[list[Version]]:
        version_index = 0
        between_versions:list[Version] = []
        output:list[list[Version]] = []
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

    def print_exception_list(self, trace:Trace, versions:Sequence["Version"], domain:"Domain.Domain") -> bool:
        '''
        Prints all exceptions and traces in list and raises an exception at the end if the list has any items.
        '''
        texts:list[str] = list(trace.stringify())
        if trace.has_exceptions:
            if (log := domain.logs.get("structure_log")) is not None and log.supports_type(log, str):
                log.write(f"-------- {trace.exception_count} EXCEPTIONS IN {self.name} ON {", ".join(version.name for version in versions)} --------\n\n")
                log.write("\n".join(texts))
            for text in texts:
                print(text)
        return len(trace._exceptions) > 0

    def ensure_not_ellipsis[a](self, data:a|EllipsisType, trace:Trace, versions:Sequence["Version"], domain:"Domain.Domain") -> a:
        if self.print_exception_list(trace, versions, domain) or data is ...:
            raise TablifierError(self)
        else:
            return data

    def tablify(self, all_versions:list[Version], domain:"Domain.Domain") -> None:
        versions = self.version_provider.version_provider.get_versions(all_versions, supports_dataminer_collection=self.dataminer_collection)
        versions_structure_infos = [(version, self.dataminer_collection.get_structure_info(version)) for version in versions]
        structure_environment = StructureEnvironment(EnvironmentType.comparing, domain)
        between_versions = self._get_versions_between(all_versions, versions)
        tests = get_tests(domain)
        data_files:tuple[tuple[int, Any], ...]
        if self.name in tests:
            test = tests[self.name]
            comparison_environment = ComparisonEnvironment(structure_environment, list(repeat(versions_structure_infos[0], len(test.data))), between_versions)
            data_files = tuple(enumerate(test.data))
        else:
            test = None
            comparison_environment = ComparisonEnvironment(structure_environment, versions_structure_infos, between_versions)
            data_files = tuple((branch, self.structure.get_containerized_from_raw(self.dataminer_collection.get_data_file(version), version, comparison_environment[branch])) for branch, version in enumerate(versions))
        trace = Trace()
        comparison, _, _ = self.structure.compare(tuple(data_files), trace, comparison_environment)
        comparison = self.ensure_not_ellipsis(comparison, trace, versions, domain)
        if test is not None:
            comparison = test.result_func(comparison)
        if test is not None and test.result is not None:
            if test.result != comparison:
                print("Test failed!")
                print(f"Comparison result: {repr(comparison)}")
                print(f"Expected value: {repr(test.result)}")
            else:
                print("Test passed.")
        if test is None:
            if self.structure.delegate is None:
                output = self.ensure_not_ellipsis(self.structure.print_comparison(comparison, tuple(range(len(comparison_environment))), trace, comparison_environment), trace, versions, domain)
            else:
                output = self.ensure_not_ellipsis(self.structure.delegate.print_comparison(comparison, tuple(range(len(comparison_environment))), trace, comparison_environment), trace, versions, domain)
            with open(self.path, "wt", encoding="UTF8") as f:
                f.write(output)
