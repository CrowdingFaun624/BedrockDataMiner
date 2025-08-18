import importlib
from collections import Counter
from datetime import datetime
from pathlib import Path
from typing import Callable, Final, Mapping

import Domain.Domain as Domain
from Component.ComponentObject import ComponentObject
from Component.Field.Errors import Errors
from Component.Group import (
    ComponentFile,
    Group,
    GroupDirectory,
    GroupFile,
    GroupObject,
    ScriptFile,
)
from Component.ImporterFinalize import finalize_all
from Component.Parser import parse_file
from Component.Reader import Reader
from Component.Scope import EMPTY_SCOPE
from Dataminer.AbstractDataminerCollection import AbstractDataminerCollection
from Serializer.Serializer import SerializerCreator
from Structure.StructureTag import StructureTag
from Tablifier.Tablifier import Tablifier
from Utilities.MemoryUsage import memory_usage
from Utilities.Trace import Trace
from Version.Version import Version
from Version.VersionTag.VersionTag import VersionTag

DEBUG:Final[bool] = False

def parse_groups(domain:"Domain.Domain", path:Path, parent:GroupObject|None) -> GroupObject|None:
    path_name = f"{domain.name}!{path.relative_to(domain.assets_directory).as_posix()}"
    if path.is_file():
        if path.suffix.lower() == ".cmp":
            output = ComponentFile(path, path_name, parent, domain)
            return output
        elif path.suffix.lower() == ".py":
            relative_name = path.relative_to(domain.assets_directory).as_posix()
            module_name = f"_domains.{domain.name}.{relative_name.replace("/", ".").removesuffix(".py")}"
            return ScriptFile(path, path_name, parent, domain, module_name)
    elif path.is_dir():
        children:dict[str,GroupObject] = {}
        output = GroupDirectory(path, path_name, parent, children)
        for subpath in path.iterdir():
            subgroup = parse_groups(domain, subpath, output)
            if subgroup is None: continue
            children[subpath.name.rsplit(".")[0]] = subgroup # the rsplit removes the suffix
        return output
    else:
        return None

def get_object_dictionary[T: ComponentObject, F=T](all_objects:list[object], object_type:type[T], transform:Callable[[T],F]=lambda item: item) -> Mapping[str,F]:
    """
    Constructs a dictionary of ComponentObjects of a specific type.

    :param all_objects: A list of every Component Field's final.
    :param object_type: The type of object to filter.
    """
    final_names:dict[tuple[str,str],F] = {}
    primary_names:Counter[str] = Counter()
    for final in all_objects:
        if isinstance(final, object_type):
            final_names[final.name, final.full_name] = transform(final)
            primary_names[final.name] += 1
    return {(secondary_name if primary_names[primary_name] > 1 else primary_name): object for (primary_name, secondary_name), object in final_names.items()}

def import_all(primary_domain:"Domain.Domain") -> bool:
    """
    :param primary_domain: The Domain (and its dependencies) to modify.
    :returns: A bool that if True, means that there is an error.
    """
    all_domains = primary_domain.get_cascading_dependencies(set())
    all_group_files:Mapping["Domain.Domain", list[GroupFile]] = {domain: [] for domain in all_domains}
    all_bases:dict["Domain.Domain", GroupDirectory] = {}
    for domain in all_domains:
        base_group_file = parse_groups(domain, domain.assets_directory, None)
        assert isinstance(base_group_file, GroupDirectory)
        all_bases[domain] = base_group_file
        all_group_files[domain].extend(base_group_file.get_all_children())
        domain.add_file_tree(base_group_file)

    for domain in all_domains:
        domain.import_scripts()

    error = Errors.fine # used to determine if anything should be returned
    all_groups:dict["Domain.Domain", list[Group]] = {domain: [] for domain in all_domains}
    for domain, group_files in all_group_files.items():
        for group_file in group_files:
            if DEBUG:
                print("parsing", group_file)
            if isinstance(group_file, ComponentFile):
                with open(group_file.path, "rt", encoding="utf-8") as f:
                    reader = Reader(f.read(), domain.name + "!" + group_file.path.relative_to(domain.assets_directory).as_posix().removesuffix(".cmp"), group_file.path)
                group = group_file.group = parse_file(reader, domain, group_file.path)
                group.group_file = group_file
                all_groups[domain].append(group)
            elif isinstance(group_file, ScriptFile):
                importlib.import_module(group_file.module_name)

    trace = Trace()
    for domain, groups in all_groups.items():
        with trace.enter(domain, domain.name, ...):
            for group in groups:
                if DEBUG:
                    print("set_field", group)
                with trace.enter(group, group.name, ...):
                    group.settings.set_field(domain, group, trace)
                    for index, (field_name, field) in enumerate(group.fields.items()):
                        # do even if abstract
                        field.set_field(group, field_name, field_name, index, trace, is_inline=False)

    for domain, groups in all_groups.items():
        with trace.enter(domain, domain.name, ...):
            for group in groups:
                if DEBUG:
                    print("create_field", group)
                with trace.enter(group, group.name, ...):
                    for field_name, field_factory in group.fields.items():
                        if not field_factory.abstract:
                            field_factory.create_field(EMPTY_SCOPE, set(), trace)

    for domain, groups in all_groups.items():
        with trace.enter(domain, domain.name, ...):
            domain.remove_file_tree()
            for group in groups:
                if DEBUG:
                    print("create_final", group)
                with trace.enter(group, group.name, ...):
                    for field_name, field in group.fields.items():
                        if not field.abstract:
                            field.create_final(EMPTY_SCOPE, trace)

    for domain, groups in all_groups.items():
        with trace.enter(domain, domain.name, ...):
            for group in groups:
                if DEBUG:
                    print("link_final", group)
                with trace.enter(group, group.name, ...):
                    finals:dict[str,object] = {}
                    group.finals = finals
                    for field_name, field in group.fields.items():
                        if not field.abstract:
                            finals[field_name], _ = field.link_final(EMPTY_SCOPE, trace)

    for domain, groups in all_groups.items():
        with trace.enter(domain, domain.name, ...):
            for group in groups:
                if DEBUG:
                    print("finalize", group)
                with trace.enter(group, group.name, ...):
                    for field_name, field in group.fields.items():
                        if not field.abstract:
                            error = error.narrow(field.finalize(EMPTY_SCOPE, trace))

    if error > Errors.finalize:
        for domain in all_domains:
            domain_finals = [final for group in all_groups[domain] for final in group.finals.values()]
            domain.set_values(
                dataminer_collections=get_object_dictionary(domain_finals, AbstractDataminerCollection),
                serializers=get_object_dictionary(domain_finals, SerializerCreator, lambda serializer: serializer.serializer),
                structure_tags=get_object_dictionary(domain_finals, StructureTag),
                tablifiers=get_object_dictionary(domain_finals, Tablifier),
                version_tags=get_object_dictionary(domain_finals, VersionTag),
                versions=get_object_dictionary(domain_finals, Version),
            )
            memory_usage.add_domain(domain)

        error = error.narrow(finalize_all(all_groups, trace))

    if trace.has_exceptions or any(group.reader.has_exceptions for groups in all_groups.values() for group in groups):
        exception_count:int = 0
        with open(primary_domain.component_log_file, "wt") as f:
            f.write(f"{datetime.now().isoformat()}\n\n") # clear
        for groups in all_groups.values():
            for group in groups:
                if group.reader.has_exceptions:
                    for exception in group.reader.stringify_exceptions():
                        print(exception)
                        with open(primary_domain.component_log_file, "at", encoding="utf-8") as f:
                            f.write(exception + "\n\n")
                        exception_count += 1
        for exception in trace.stringify():
            print(exception)
            with open(primary_domain.component_log_file, "at", encoding="utf-8") as f:
                f.write(exception + "\n\n")
            exception_count += 1
        print(f"{exception_count} total exceptions")

    if error == Errors.fine: # not designed for missing attributes due to errors.
        for domain, groups in all_groups.items():
            for group in groups:
                if DEBUG:
                    print("destroy", group)
                group.destroy()

    if error < Errors.fine:
        print(f"Failed to import ({error.name})")
    elif DEBUG:
        print("Successfully imported.")

    return error < Errors.fine
