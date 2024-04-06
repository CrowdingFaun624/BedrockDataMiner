from typing import Callable

import Comparison.ComparerImporter.ComparerIntermediate as ComparerIntermediate
import Comparison.ComparerImporter.ComparerTyping as ComparerTyping
import Comparison.ComparerImporter.Intermediate as Intermediate
import Comparison.ComparerImporter.IntermediateCapabilities as IntermediateCapabilities
import Comparison.ComparerImporter.NormalizerFunctionIntermediate as NormalizerFunctionIntermediate
import Comparison.Comparer as Comparer
import Utilities.TypeVerifier as TypeVerifier

COMPARER_REQUEST_PROPERTIES = IntermediateCapabilities.CapabilitiesPattern([{"is_comparer": True}])
NORMALIZER_FUNCTION_REQUEST_PROPERTIES = IntermediateCapabilities.CapabilitiesPattern([{"is_normalizer_function": True}])

class MainIntermediate(Intermediate.Intermediate):

    class_name_article = "a Main"
    class_name = "Main"

    my_properties = IntermediateCapabilities.Capabilities(is_main=True)

    type_verifier = TypeVerifier.TypedDictTypeVerifier(
        TypeVerifier.TypedDictKeyTypeVerifier("data", "a dict", True, TypeVerifier.TypedDictTypeVerifier(
            TypeVerifier.TypedDictKeyTypeVerifier("base_comparer_section", "a str", True, str),
            TypeVerifier.TypedDictKeyTypeVerifier("imports", "a list", False, TypeVerifier.ListTypeVerifier(TypeVerifier.TypedDictTypeVerifier(
                TypeVerifier.TypedDictKeyTypeVerifier("from", "a str", True, str),
                TypeVerifier.TypedDictKeyTypeVerifier("components", "a dict", True, TypeVerifier.ListTypeVerifier(TypeVerifier.TypedDictTypeVerifier(
                    TypeVerifier.TypedDictKeyTypeVerifier("component", "a str", True, str),
                    TypeVerifier.TypedDictKeyTypeVerifier("as", "a str", False, str),
                ), list, "a dict", "a list")),
            ), list, "a dict", "a list")),
            TypeVerifier.TypedDictKeyTypeVerifier("name", "a str", True, str),
            TypeVerifier.TypedDictKeyTypeVerifier("normalizer", "a str", False, str),
            TypeVerifier.TypedDictKeyTypeVerifier("post_normalizer", "a str", False, str),
            TypeVerifier.TypedDictKeyTypeVerifier("type", "a str", True, TypeVerifier.EnumTypeVerifier((class_name,))),
        )),
        TypeVerifier.TypedDictKeyTypeVerifier("name", "a str", True, str),
        TypeVerifier.TypedDictKeyTypeVerifier("index", "an int", True, int),
    )

    def __init__(self, data:ComparerTyping.MainTypedDict, name:str, index:int) -> None:
        self.type_verifier.base_verify({"data": data, "name": name, "index": index}, ["%s \"%s\"" % (self.class_name, name)])

        self.name = name
        self.comparer_name = data["name"]
        self.base_comparer_section_str = data["base_comparer_section"]
        self.normalizer_str = data.get("normalizer", None)
        self.post_normalizer_str = data.get("post_normalizer", None)
        self.imports = data.get("imports", None)

        self.base_comparer_section:ComparerIntermediate.ComparerIntermediate|None = None
        self.normalizer:NormalizerFunctionIntermediate.NormalizerFunctionIntermediate|None = None
        self.post_normalizer:NormalizerFunctionIntermediate.NormalizerFunctionIntermediate|None = None
        self.links_to_other_intermediates:list[Intermediate.Intermediate] = []
        self.parents:list[Intermediate.Intermediate] = []
        self.final:Comparer.Comparer|None = None

        self.children_has_normalizer = False

    def set(self, intermediate_comparers:dict[str,Intermediate.Intermediate], functions:dict[str,Callable]) -> None:
        self.base_comparer_section:ComparerIntermediate.ComparerIntermediate|None = self.choose_intermediate(self.base_comparer_section_str, COMPARER_REQUEST_PROPERTIES, intermediate_comparers, ["base_comparer_section"])
        assert self.base_comparer_section is not None
        self.links_to_other_intermediates.append(self.base_comparer_section)
        self.base_comparer_section.parents.append(self)
        if self.normalizer_str is None:
            self.normalizer = None
        else:
            self.normalizer:NormalizerFunctionIntermediate.NormalizerFunctionIntermediate|None = self.choose_intermediate(self.normalizer_str, NORMALIZER_FUNCTION_REQUEST_PROPERTIES, intermediate_comparers, ["normalizer"])
            assert self.normalizer is not None
            self.links_to_other_intermediates.append(self.normalizer)
            self.normalizer.parents.append(self)
        if self.post_normalizer_str is None:
            self.post_normalizer = None
        else:
            self.post_normalizer:NormalizerFunctionIntermediate.NormalizerFunctionIntermediate|None = self.choose_intermediate(self.post_normalizer_str, NORMALIZER_FUNCTION_REQUEST_PROPERTIES, intermediate_comparers, ["post_normalizer"])
            assert self.post_normalizer is not None
            self.links_to_other_intermediates.append(self.post_normalizer)
            self.post_normalizer.parents.append(self)

    def create_final(self) -> None:
        normalizer_final = None if self.normalizer is None else self.normalizer.final
        post_normalizer_final = None if self.post_normalizer is None else self.post_normalizer.final
        self.final = Comparer.Comparer(
            name=self.comparer_name,
            normalizer=normalizer_final,
            post_normalizer=post_normalizer_final,
            base_comparer_section=None,
        )

    def link_finals(self) -> None:
        assert self.final is not None
        assert self.base_comparer_section is not None
        self.final.base_comparer_section = self.base_comparer_section.final
