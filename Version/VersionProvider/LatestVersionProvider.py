import Component.Importer as Importer
import DataMiner.AbstractDataMinerCollection as AbstractDataMinerCollection
import Version.Version as Version
import Version.VersionProvider.VersionProvider as VersionProvider


class LatestVersionProvider(VersionProvider.VersionProvider):
    
    def get_versions(self, versions: list[Version.Version], *, supports_dataminer_collection:AbstractDataMinerCollection.AbstractDataMinerCollection) -> list[Version.Version]:
        major_versions:list[Version.Version] = [] # starts out sorted newest to oldest
        has_selected_release_major_version = False
        for version in reversed(versions):
            if not version.released:
                major_versions.append(version)
                has_selected_release_major_version = False
            elif len(major_versions) == 0:
                # the last version in the version list should be a major version.
                major_versions.append(version)
            elif not has_selected_release_major_version and not version.get_order_tag().is_development_tag:
                # select the latest major release
                major_versions.append(version)
                has_selected_release_major_version = True
            else:
                continue
        version_tags_order = Importer.version_tags_order
        major_versions.reverse() # now it's sorted from oldest to newest.
        output:list[Version.Version] = []
        for major_version in major_versions:
            if major_version.released and supports_dataminer_collection.supports_version(major_version):
                output.append(major_version)
            else:
                parent_version = major_version
                while not any(child_tag.is_development_tag for child_tag in version_tags_order.get_allowed_children()[parent_version.get_order_tag()]):
                    parent_version = major_version.parent
                    assert parent_version is not None
                if parent_version is not major_version and supports_dataminer_collection.supports_version(parent_version):
                    output.append(parent_version)
                    continue
                # get the latest dev version of the major version.
                for child in reversed(parent_version.children):
                    if child.get_order_tag().is_development_tag and supports_dataminer_collection.supports_version(child):
                        output.append(child)
                        break
                else:
                    # if a version has no development
                    continue
        return output
