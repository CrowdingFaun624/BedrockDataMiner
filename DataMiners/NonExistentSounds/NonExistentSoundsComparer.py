import Comparison.ComparerImporter as ComparerImporter
import Utilities.CollapseResourcePacks as CollapseResourcePacks

comparer = ComparerImporter.load_from_file("non_existent_sounds", {"collapse_resource_packs": CollapseResourcePacks.make_interface(has_defined_in_key=False)})
