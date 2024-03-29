from typing import Callable

import Comparison.ComparerImporter.Intermediate as Intermediate
import Comparison.ComparerImporter.ComparerIntermediate as ComparerIntermediate
import Comparison.ComparerImporter.ComparerTyping as ComparerTyping
import Comparison.ComparerImporter.NormalizerFunctionIntermediate as NormalizerFunctionIntermediate
import Comparison.Comparer as Comparer

class MainIntermediate(Intermediate.Intermediate):

    def __init__(self, data:ComparerTyping.MainTypedDict, name:str, index:int) -> None:
        self.check_types(data, name, index, [
            ("base_comparer_section", str, "a str", True),
            ("imports", list, "a list", False),
            ("name", str, "a str", True),
            ("normalizer", str, "a str", False),
            ("post_normalizer", str, "a str", False),
            ("type", str, "a str", True),
        ])
        if data["type"] != "Main":
            raise ValueError("Key \"type\" of Main \"%s\" is not \"Main\"!" % (name))
        if "imports" in data:
            if not isinstance(data["imports"], list):
                raise TypeError("Key \"imports\" is not a list!")
            self.check_imports_type(data["imports"], name)

        self.name = name
        self.comparer_name = data["name"]
        self.base_comparer_section_str = data["base_comparer_section"]
        self.normalizer_str = None if "normalizer" not in data else data["normalizer"]
        self.post_normalizer_str = None if "post_normalizer" not in data else data["post_normalizer"]
        self.imports = None if "imports" not in data else data["imports"]

        self.base_comparer_section:ComparerIntermediate.ComparerIntermediate|None = None
        self.normalizer:NormalizerFunctionIntermediate.NormalizerFunctionIntermediate|None = None
        self.post_normalizer:NormalizerFunctionIntermediate.NormalizerFunctionIntermediate|None = None
        self.links_to_other_intermediates:list[Intermediate.Intermediate] = []
        self.parents:list[Intermediate.Intermediate] = []
        self.final:Comparer.Comparer|None = None

        self.children_has_normalizer = False

    def check_imports_type(self, imports:list[ComparerTyping.ImportTypedDict], name:str) -> None:
        for index, imported_comparer in enumerate(imports):
            if not isinstance(imported_comparer, dict):
                raise TypeError("Item %i of key \"imports\" of Main \"%s\" is not a dict!" % (index, name))
            unrecognized_keys = [key for key in imported_comparer.keys() if key not in ("from", "components")]
            if len(unrecognized_keys) > 0:
                raise KeyError("Unrecognized key(s) in item %i of key \"imports\" of Main \"%s\": [%s]" % (index, name, ", ".join(unrecognized_keys)))
            if "from" not in imported_comparer:
                raise KeyError("Key \"from\" is not in item %i of key \"imports\" of Main \"%s\"!" % (index, name))
            if "components" not in imported_comparer:
                raise KeyError("Key \"components\" is not in item %i of key \"imports\" of Main \"%s\"!" % (index, name))
            if not isinstance(imported_comparer["from"], str):
                raise TypeError("Key \"from\" of item %i of key \"imports\" of Main \"%s\" is not a str!" % (index, name))
            if not isinstance(imported_comparer["components"], list):
                raise TypeError("Key \"components\" of item %i of key \"imports\" of Main \"%s\" is not a list!" % (index, name))
            for component_index, imported_component in enumerate(imported_comparer["components"]):
                if not isinstance(imported_component, dict):
                    raise TypeError("Item %i of key \"components\" of item %i of key \"imports\" of Main \"%s\" is not a dict!" % (component_index, index, name))
                unrecognized_keys = [key for key in imported_component.keys() if key not in ("component", "as")]
                if len(unrecognized_keys) > 0:
                    raise KeyError("Unrecognized key(s) in item %i of key \"components\" of item %i of key \"imports\" of Main \"%s\": [%s]" % (component_index, index, name, ", ".join(unrecognized_keys)))
                if "component" not in imported_component:
                    raise KeyError("Key \"component\" is not in item %i of key \"components\" of item %i of key \"imports\" of Main \"%s\"!" % (component_index, index, name))
                if not isinstance(imported_component["component"], str):
                    raise TypeError("Key \"component\" of item %i of key \"components\" of item %i of key \"imports\" of Main \"%s\" is not a str!" % (component_index, index, name))
                if "as" in imported_component and not isinstance(imported_component["as"], str):
                    raise TypeError("Key \"as\" of item %i of key \"components\" of item %i of key \"imports\" of Main \"%s\" is not a str!" % (component_index, index, name))

    def set(self, intermediate_comparers:dict[str,Intermediate.Intermediate], functions:dict[str,Callable]) -> None:
        self.base_comparer_section:ComparerIntermediate.ComparerIntermediate|None = self.choose_intermediate(self.base_comparer_section_str, ComparerIntermediate.ComparerIntermediate, "a Comparer", intermediate_comparers, ["base_comparer_section"])
        assert self.base_comparer_section is not None
        self.links_to_other_intermediates.append(self.base_comparer_section)
        self.base_comparer_section.parents.append(self)
        if self.normalizer_str is None:
            self.normalizer = None
        else:
            self.normalizer:NormalizerFunctionIntermediate.NormalizerFunctionIntermediate|None = self.choose_intermediate(self.normalizer_str, NormalizerFunctionIntermediate.NormalizerFunctionIntermediate, "a NormalizerFunction", intermediate_comparers, ["normalizer"])
            assert self.normalizer is not None
            self.links_to_other_intermediates.append(self.normalizer)
            self.normalizer.parents.append(self)
        if self.post_normalizer_str is None:
            self.post_normalizer = None
        else:
            self.post_normalizer:NormalizerFunctionIntermediate.NormalizerFunctionIntermediate|None = self.choose_intermediate(self.post_normalizer_str, NormalizerFunctionIntermediate.NormalizerFunctionIntermediate, "a NormalizerFunction", intermediate_comparers, ["post_normalizer"])
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
