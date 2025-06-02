from functools import cache
from itertools import repeat
from types import EllipsisType
from typing import Any, Callable, Sequence

import Dataminer.AbstractDataminerCollection as AbstractDataminerCollection
import Domain.Domain as Domain
import Structure.Difference as D
import Structure.IterableContainer as ICon
import Structure.SimpleContainer as SCon
import Structure.StructureBase as StructureBase
import Structure.StructureEnvironment as StructureEnvironment
import Utilities.Exceptions as Exceptions
import Utilities.FileManager as FileManager
import Utilities.Trace as Trace
import Version.Version as Version
import Version.VersionProvider.VersionProvider as VersionProvider
from Utilities.File import FakeFile


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
    empty = SCon.SCon("", domain)
    false = ICon.icon_from_list(((empty, SCon.SCon(0, domain)),), {empty: SCon.SCon(0, domain)})
    true  = ICon.icon_from_list(((empty, SCon.SCon(1, domain)),), {empty: SCon.SCon(1, domain)})
    def idon(bundles:dict[tuple[int,...],bool]) -> ICon.IDon:
        diff = D.Diff({bundle: (false, true)[value].as_don(bundle) for bundle, value in bundles.items()}, False)
        return ICon.idon_from_list((diff for bundle in bundles.keys() for branch in bundle), {branch: (false, true)[value] for bundle, value in bundles.items() for branch in bundle})
    name:Callable[[str], SCon.SCon[str]] = lambda name: SCon.SCon(name, domain)
    input1 = {name("Ava"): false, name("Bella"): false, name("Chloe"): false, name("Daisy"): false, name("Emma"): false, name("Fiona"): false, name("Grace"): false, name("Hannah"): false, name("Isabella"): false,                                                                                    }
    input2 = {name("Ava"): false, name("Bella"): false, name("Chloe"): false, name("Daisy"): true , name("Emma"): true , name("Fiona"): true ,                                                                       name("Julia"): false, name("Kayla"): false, name("Luna"): false,                   }
    input3 = {name("Ava"): false, name("Bella"): true ,                       name("Daisy"): false, name("Emma"): true ,                       name("Grace"): false, name("Hannah"): true ,                          name("Julia"): false, name("Kayla"): true ,                      name("Mia"): false}
    input1_container = ICon.icon_from_list(input1.items(), input1)
    input2_container = ICon.icon_from_list(input2.items(), input2)
    input3_container = ICon.icon_from_list(input3.items(), input3)
    output = D.Diff({(0, 1, 2): ICon.idon_from_list([
        (D.Diff({(0, 1, 2): SCon.sdon_from_bundles({(0, 1, 2): "Ava"}, domain)}, False), D.Diff({(0, 1, 2): idon({(0, 1, 2): False})}, False)),
        (D.Diff({(0, 1, 2): SCon.sdon_from_bundles({(0, 1, 2): "Bella"}, domain)}, False), D.Diff({(0, 1, 2): idon({(0, 1): False, (2,): True})}, True)),
        (D.Diff({(0, 1, 2): SCon.sdon_from_bundles({(0, 1, 2): "Chloe"}, domain)}, False), D.Diff({(0, 1, 2): idon({(0, 1): False})}, True)),
        (D.Diff({(0, 1, 2): SCon.sdon_from_bundles({(0, 1, 2): "Daisy"}, domain)}, False), D.Diff({(0, 1, 2): idon({(0,): False, (1,): True, (2,): False})}, True)),
        (D.Diff({(0, 1, 2): SCon.sdon_from_bundles({(0, 1, 2): "Emma"}, domain)}, False), D.Diff({(0, 1, 2): idon({(0,): False, (1, 2): True})}, True)),
        (D.Diff({(0, 1): SCon.sdon_from_bundles({(0, 1): "Fiona"}, domain)}, False), D.Diff({(0, 1, 2): idon({(0,): False, (1,): True})}, True)),
        (D.Diff({(0, 2): SCon.sdon_from_bundles({(0, 2): "Grace"}, domain)}, False), D.Diff({(0, 1, 2): idon({(0, 2): False})}, False)),
        (D.Diff({(0, 2): SCon.sdon_from_bundles({(0, 2): "Hannah"}, domain)}, False), D.Diff({(0, 1, 2): idon({(0,): False, (2,): True})}, True)),
        (D.Diff({(0,): SCon.sdon_from_bundles({(0,): "Isabella"}, domain)}, False), D.Diff({(0, 1, 2): idon({(0,): False})}, True)),
        (D.Diff({(1, 2): SCon.sdon_from_bundles({(1, 2): "Julia"}, domain)}, False), D.Diff({(0, 1, 2): idon({(1, 2): False})}, True)),
        (D.Diff({(1, 2): SCon.sdon_from_bundles({(1, 2): "Kayla"}, domain)}, False), D.Diff({(0, 1, 2): idon({(1,): False, (2,): True})}, True)),
        (D.Diff({(1,): SCon.sdon_from_bundles({(1,): "Luna"}, domain)}, False), D.Diff({(0, 1, 2): idon({(1,): False})}, True)),
        (D.Diff({(2,): SCon.sdon_from_bundles({(2,): "Mia"}, domain)}, False), D.Diff({(0, 1, 2): idon({(2,): False})}, True)),
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
        #         "Bella": D.Diff(3, {(0, 1): "Bike", (2,): "Bice"}),
        #         D.Diff(3, {(0, 1): "Chloe"}): D.Diff(3, {(0, 1): "Case"}),
        #         "Daisy": D.Diff(3, {(0,): "Dish", (1,): "Dosh", (2,): "Dish"}),
        #         "Emma": D.Diff(3, {(0,): "Exam", (1, 2): "Emam"}),
        #         D.Diff(3, {(0, 1): "Fiona"}): D.Diff(3, {(0,): "Fight", (1,): "Fhght"}),
        #         D.Diff(3, {(0, 2): "Grace"}): D.Diff(3, {(0, 2): "Golf"}),
        #         D.Diff(3, {(0, 2): "Hannah"}): D.Diff(3, {(0,): "Hole", (2,): "Hale"}), # this is desired behavior. If it had an Object child, it would be combined.
        #         D.Diff(3, {(0,): "Isabella"}): D.Diff(3, {(0,): "Iron"}),
        #         D.Diff(3, {(1, 2): "Julia"}): D.Diff(3, {(1, 2): "Joint"}),
        #         D.Diff(3, {(1, 2): "Kayla"}): D.Diff(3, {(1,): "Key", (2,): "Keg"}),
        #         D.Diff(3, {(1,): "Luna"}): D.Diff(3, {(1,): "Ladder"}),
        #         D.Diff(3, {(2,): "Mia"}): D.Diff(3, {(2,): "Model"}),
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
        #         D.Diff(3, {(0, 1): "Bella", (2,): "Bello"}): 1,
        #         D.Diff(3, {(0, 1): "Chloe"}): D.Diff(3, {(0, 1): 2}),
        #         D.Diff(3, {(0,): "Daisy", (1,): "Daist", (2,): "Daisy"}): 3,
        #         D.Diff(3, {(0,): "Emma", (1, 2): "Emmm"}): 4,
        #         D.Diff(3, {(0,): "Fiona", (1,): "Fionl"}): D.Diff(3, {(0, 1): 5}),
        #         D.Diff(3, {(0, 2): "Grace"}): D.Diff(3, {(0, 2): 6}),
        #         D.Diff(3, {(0,): "Hannah", (2,): "Hannoh"}): D.Diff(3, {(0, 2): 7}),
        #         D.Diff(3, {(0,): "Isabella"}): D.Diff(3, {(0,): 8}),
        #         D.Diff(3, {(1, 2): "Julia"}): D.Diff(3, {(1, 2): 9}),
        #         D.Diff(3, {(1,): "Kayla", (2,): "Kayli"}): D.Diff(3, {(1, 2): 10}),
        #         D.Diff(3, {(1,): "Luna"}): D.Diff(3, {(1,): 11}),
        #         D.Diff(3, {(2,): "Mia"}): D.Diff(3, {(2,): 12}),
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
        #         D.Diff(3, {(0, 1): "Bella", (2,): "Bello"}),
        #         D.Diff(3, {(0, 1): "Chloe"}),
        #         D.Diff(3, {(0,): "Daisy", (1,): "Daist", (2,): "Daisy"}),
        #         D.Diff(3, {(0,): "Emma", (1,2): "Emmm"}),
        #         D.Diff(3, {(0,): "Fiona", (1,): "Fionl"}),
        #         D.Diff(3, {(0, 2): "Grace"}),
        #         D.Diff(3, {(0,): "Hannah", (2,): "Hannoh"}),
        #         D.Diff(3, {(0,): "Isabella"}),
        #         D.Diff(3, {(1,2): "Julia"}),
        #         D.Diff(3, {(1,): "Kayla", (2,): "Kayli"}),
        #         D.Diff(3, {(1,): "Luna"}),
        #         D.Diff(3, {(2,): "Mia"}),
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
        #         {"n": "Bella", "v": D.Diff(3, {(0, 1): 0, (2,): 1})},
        #         D.Diff(3, {(0, 1): {"n": "Chloe", "v": 0}}),
        #         {"n": "Daisy", "v": D.Diff(3, {(0,): 0, (1,): 1, (2,): 0})},
        #         {"n": "Emma", "v": D.Diff(3, {(0,): 0, (1, 2): 1})},
        #         D.Diff(3, {(0, 1): {"n": "Fiona", "v": D.Diff(3, {(0,): 0, (1,): 1})}}),
        #         D.Diff(3, {(0, 2): {"n": "Grace", "v": 0}}),
        #         D.Diff(3, {(0, 2): {"n": "Hannah", "v": D.Diff(3, {(0, 1): 0, (2,): 1})}}),
        #         D.Diff(3, {(0,): {"n": "Isabella", "v": 0}}),
        #         D.Diff(3, {(1, 2): {"n": "Julia", "v": 0}}),
        #         D.Diff(3, {(1, 2): {"n": "Kayla", "v": D.Diff(3, {(0, 1): 0, (2,): 1})}}),
        #         D.Diff(3, {(1,): {"n": "Luna", "v": 0}}),
        #         D.Diff(3, {(2,): {"n": "Mia", "v": 0}})
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
        #         "b": [0, D.Diff(3, {(1,2): 1}), D.Diff(3, {(2,): 2})],
        #         "c": [0, D.Diff(3, {(0,1): 1}), D.Diff(3, {(0,): 2})],
        #         "d": [D.Diff(3, {(0,): 0, (1,): 1, (2,): 2}), D.Diff(3, {(0, 1): 1, (2,): 3}), D.Diff(3, {(0,): 2, (1, 2): 3})],
        #         "e": [D.Diff(3, {(1,): 0, (2,): 1})],
        #         "f": [D.Diff(3, {(0,): 0, (1,): 1})],
        #         "g": [{"":0}, {"":1}, {"":2}],
        #         "h": [{"":0}, D.Diff(3, {(1, 2): {"":1}}), D.Diff(3, {(2,): {"":2}})],
        #         "i": [{"":0}, D.Diff(3, {(0, 1): {"":1}}), D.Diff(3, {(0,): {"":2}})],
        #         "j": [{"":D.Diff(3, {(0,): 0, (1,): 1, (2,): 2})}, {"":D.Diff(3, {(0, 1): 1, (2,): 3})}, {"":D.Diff(3, {(0,): 2, (1, 2): 3})}],
        #         "k": [D.Diff(3, {(1, 2): {"":D.Diff(3, {(0, 1): 0, (2,): 1})}})],
        #         "l": [D.Diff(3, {(0, 1): {"":D.Diff(3, {(0,): 0, (1,): 1})}})],
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
        #         "a": ["Ava", D.Diff(3, {(0,): "Bella", (1,): "Bello", (2,): "Bella"})],
        #         "b": [D.Diff(3, {(0,): "Ava", (1, 2): "Aba"}), D.Diff(3, {(0, 1): "Bella", (2,): "Bello"})],
        #         "c": [D.Diff(3, {(0, 1): "Ava"}), D.Diff(3, {(1, 2): "Bella"})],
        #         "d": [D.Diff(3, {(0,): "Ava", (1,): "Aba"}), D.Diff(3, {(1,): "Bella", (2,): "Bello"})],
        #         "e": [D.Diff(3, {(0, 2): "Ava"}), D.Diff(3, {(0,): "Bella", (2,): "Bello"})],
        #         "f": [D.Diff(3, {(0,): "Ava"})],
        #         "g": [D.Diff(3, {(1,): "Ava"})],
        #         "h": [D.Diff(3, {(2,): "Ava"})],
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
        #         "b": D.Diff(3, {(0,): 0, (1,): 1, (2,): 2}),
        #         "c": D.Diff(3, {(0,): 0, (1, 2): 1}),
        #         "d": D.Diff(3, {(0, 1): 0, (2,): 2}),
        #         "e": "Egg",
        #         "f": D.Diff(3, {(0,): 0, (1, 2): "Egg"}),
        #         "g": D.Diff(3, {(0,): "Egg", (1,): 0, (2,): "Egg"}),
        #         "h": D.Diff(3, {(0, 1): "Egg", (2,): 0}),
        #         "i": {"": D.Diff(3, {(0,): "Egg", (1,): "Egh", (2,): "Egi"})},
        #         "j": D.Diff(3, {(0,): "Egg", (1, 2): {"": D.Diff(3, {(0, 1): "Egg", (2,): "Egh"})}}),
        #         "k": D.Diff(3, {(0,): {"": "Egg"}, (1,): "Egg", (2,): {"": "Egg"}}),
        #         "l": D.Diff(3, {(0, 1): {"": "Egg"}, (2,): "Egg"}),
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
        #         "b": D.Diff(3, {(0, 1): 0, (2,): 1}),
        #         "c": D.Diff(3, {(0,): 0, (1, 2): 1}),
        #         "d": D.Diff(3, {(0,): 0, (1,): 1, (2,): 0}),
        #         "e": {"":0},
        #         "f": {"":D.Diff(3, {(0, 1): 0, (2,): 1})},
        #         "g": {"":D.Diff(3, {(0,): 0, (1, 2): 1})},
        #         "h": {"":D.Diff(3, {(0,): 0, (1,): 1, (2,): 0})},
        #     },
        #     lambda data: {key: (value.data if isinstance(value, FileDiff) else value.read(None)) for key, value in data.items()}
        # ),
    }

class Tablifier():

    __slots__ = (
        "dataminer_collection",
        "file_name",
        "name",
        "path",
        "structure",
        "version_provider",
    )

    def __init__(self, name:str, file_name:str) -> None:
        self.name = name
        self.file_name = file_name
        self.path = FileManager.OUTPUT_DIRECTORY.joinpath(self.file_name)

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

    def print_exception_list(self, trace:Trace.Trace, versions:Sequence["Version.Version"], domain:"Domain.Domain") -> bool:
        '''
        Prints all exceptions and traces in list and raises an exception at the end if the list has any items.
        '''
        texts:list[str] = trace.stringify()
        if len(texts) > 0:
            if (log := domain.logs.get("structure_log")) is not None and log.supports_type(log, str):
                log.write(f"-------- {len(texts)} EXCEPTIONS IN {self.name} ON {", ".join(version.name for version in versions)} --------\n\n")
                log.write("\n".join(texts))
            for text in texts:
                print(text)
        return len(trace._exceptions) > 0

    def ensure_not_ellipsis[a](self, data:a|EllipsisType, trace:Trace.Trace, versions:Sequence["Version.Version"], domain:"Domain.Domain") -> a:
        if self.print_exception_list(trace, versions, domain) or data is ...:
            raise Exceptions.TablifierError(self)
        else:
            return data

    def tablify(self, all_versions:list[Version.Version], domain:"Domain.Domain") -> None:
        versions = self.version_provider.get_versions(all_versions, supports_dataminer_collection=self.dataminer_collection)
        versions_structure_infos = [(version, self.dataminer_collection.get_structure_info(version)) for version in versions]
        structure_environment = StructureEnvironment.StructureEnvironment(StructureEnvironment.EnvironmentType.comparing, domain)
        between_versions = self._get_versions_between(all_versions, versions)
        tests = get_tests(domain)
        data_files:tuple[tuple[int, Any], ...]
        if self.name in tests:
            test = tests[self.name]
            comparison_environment = StructureEnvironment.ComparisonEnvironment(structure_environment, None, list(repeat(versions_structure_infos[0], len(test.data))), between_versions)
            data_files = tuple(enumerate(test.data))
        else:
            test = None
            comparison_environment = StructureEnvironment.ComparisonEnvironment(structure_environment, None, versions_structure_infos, between_versions)
            data_files = tuple((branch, self.structure.get_containerized_from_raw(self.dataminer_collection.get_data_file(version), version, comparison_environment[branch])) for branch, version in enumerate(versions))
        trace = Trace.Trace()
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
                output = self.ensure_not_ellipsis(self.structure.print_comparison(comparison, trace, comparison_environment), trace, versions, domain)
            else:
                output = self.ensure_not_ellipsis(self.structure.delegate.print_comparison(comparison, trace, comparison_environment), trace, versions, domain)
            with open(self.path, "wt", encoding="UTF8") as f:
                f.write(output)
