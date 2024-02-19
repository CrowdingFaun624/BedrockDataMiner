import Comparison.ComparerImporter as ComparerImporter
import Utilities.CollapseResourcePacks as CollapseResourcePacks

comparer = ComparerImporter.load_from_file("music_definitions", {"collapse_resource_packs": CollapseResourcePacks.make_interface()})
