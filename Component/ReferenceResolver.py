from types import EllipsisType
from typing import TYPE_CHECKING, Sequence

import Domain.Domain as Domain
import Domain.Domains as Domains
from Component.Field.Errors import Errors
from Component.Field.FieldFactory import FieldFactory
from Component.Group import ComponentFile, GroupDirectory, GroupObject
from Component.Scope import Scope
from Utilities.Trace import Trace

if TYPE_CHECKING:
    from Component.Field.Field import FieldFactory

def resolve_domain_reference(source:FieldFactory, domain_name:str|None, memo:set["FieldFactory"], trace:Trace, ignore_alias:"FieldFactory|None"=None) -> tuple["Domain.Domain|EllipsisType", Errors]:
    """
    Returns a Domain from a reference.

    :param source: The FieldFactory of the Field that called this function.
    :param domain_name: The Domain name specified in the reference.
    """
    error = Errors.fine
    if domain_name is None:
        return source.group.domain, error
    elif (domain_field_factory := source.group.settings.aliases.domain_aliases.get(domain_name)) is not None and domain_field_factory is not ignore_alias:
        if domain_field_factory in memo:
            trace.exception(RuntimeError(f"Domain alias {domain_name} references itself"))
            error = error.narrow(Errors.create_field)
            return ..., error
        error = error.narrow(domain_field_factory.error)
        memo.add(domain_field_factory)
        domain_field, new_error = domain_field_factory.create_field(Scope.new_empty(), memo, trace)
        error = error.narrow(new_error)
        if error <= Errors.create_field:
            return ..., error
        assert domain_field is not ...
        error = error.narrow(domain_field.create_final(trace))
        if error <= Errors.create_final:
            return ..., error
        domain, _, new_error = domain_field.link_final(trace)
        error = error.narrow(new_error)
        if error <= Errors.link_final:
            return ..., error
        assert domain is not ...
        return domain, error
    else:
        domain = Domains.domains.get(domain_name, ...)
        if domain is ...:
            error = error.narrow(source.group.settings.aliases.error)
            if error <= Errors.create_field:
                return ..., error
            trace.exception(RuntimeError(f"Unrecognized Domain {domain_name}"))
            error = error.narrow(Errors.create_field)
            return ..., error
    if domain is not source.group.domain and domain not in source.group.domain.dependencies:
        trace.exception(RuntimeError(f"{domain} is not a dependency of {source.group.domain}"))
        error = error.narrow(Errors.create_field)
        return ..., error
    return domain, error

def resolve_group_reference[T:GroupObject](
    source:FieldFactory,
    domain_name:str|None,
    group_path:Sequence[str],
    memo:set["FieldFactory"],
    trace:Trace,
    allowed_type:type[T]=ComponentFile,
    ignore_alias:"FieldFactory|None"=None,
) -> tuple[T|EllipsisType, Errors]:
    """
    Returns a Group from a reference

    :param source: The FieldFactory of the Field that called this function.
    :param domain_name: The Domain name specified in the reference.
    :param group_path: The forward slash–delimited Group path.
    :param allowed_type: The allowed type of GroupObject.
    """
    error = Errors.fine
    domain, new_error = resolve_domain_reference(source, domain_name, set(), trace)
    if (error := error.narrow(new_error)) <= Errors.create_field:
        return ..., error
    assert domain is not ...
    if len(group_path) == 0: # refers to same Group
        if domain_name is not None:
            trace.exception(RuntimeError("Cannot specify a Domain without a Group"))
            error = error.narrow(Errors.create_field)
        if not isinstance(source.group.group_file, allowed_type):
            trace.exception(RuntimeError(f"Must be a {allowed_type.name}"))
            error = error.narrow(Errors.create_field)
            return ..., error
        return source.group.group_file, error
    first_item = group_path[0]

    current_group_file:GroupObject|EllipsisType
    skip_first_item:bool = False
    if domain_name is not None:
        current_group_file = domain.file_tree
    elif first_item == ".":
        current_group_file = source.group.group_file
        skip_first_item = True
    elif (aliased_group_field_factory := source.group.settings.aliases.group_aliases.get(first_item)) is not None and aliased_group_field_factory is not ignore_alias:
        if aliased_group_field_factory in memo:
            trace.exception(RuntimeError(f"Group alias {group_path} references itself"))
            error = error.narrow(Errors.create_field)
            return ..., error
        aliased_group_field, new_error = aliased_group_field_factory.create_field(Scope.new_empty(), memo, trace)
        memo.add(aliased_group_field_factory)
        error = error.narrow(new_error)
        if error <= Errors.create_field:
            return ..., error
        assert aliased_group_field is not ...
        error = error.narrow(aliased_group_field.create_final(trace))
        if error <= Errors.create_final:
            return ..., error
        aliased_group, _, new_error = aliased_group_field.link_final(trace)
        error = error.narrow(new_error)
        if error <= Errors.link_final:
            return ..., error
        assert aliased_group is not ...
        current_group_file = aliased_group.group_file
        skip_first_item = True
    else:
        current_group_file = domain.file_tree # from a reference with no Domain declared, just get the base directory if nothing else happens.
    for index, item in enumerate(group_path):
        if skip_first_item and index == 0: continue
        if item == ".":
            pass
        elif item == "..":
            current_group_file, new_error = current_group_file.get_parent(trace)
            if (error := error.narrow(new_error)) <= Errors.create_field:
                return ..., error
        else:
            if not isinstance(current_group_file, GroupDirectory):
                trace.exception(RuntimeError(f"Cannot get child of {current_group_file}"))
                error = error.narrow(Errors.create_field)
                return ..., error
            current_group_file, new_error = current_group_file.get_child(item, trace)
            if (error := error.narrow(new_error)) <= Errors.create_field:
                return ..., error
        assert current_group_file is not ...
    if not isinstance(current_group_file, allowed_type):
        trace.exception(RuntimeError(f"Must be a {allowed_type.name}"))
        error = error.narrow(Errors.create_field)
        return ..., error
    return current_group_file, error

def resolve_field_reference(source:FieldFactory, domain_name:str|None, group_path:Sequence[str], field_name:str, trace:Trace) -> tuple["FieldFactory|EllipsisType", Errors]:
    """
    Returns a Field from a reference.

    :param source: The FieldFactory of the Field that called this function.
    :param domain_name: The Domain name specified in the reference.
    :param group_path: The forward slash–delimited Group path.
    :param field_name: The name of the Field in the Group.
    """
    error = Errors.fine
    referenced_group_file, new_error = resolve_group_reference(source, domain_name, group_path, set(), trace, ComponentFile)
    error = error.narrow(new_error)
    if referenced_group_file is ...:
        return ..., error
    referenced_group = referenced_group_file.group
    if referenced_group is ...:
        return ..., error
    error = error.narrow(referenced_group.error)
    if error <= Errors.create_field:
        return ..., error
    if (output := referenced_group.fields.get(field_name)) is None:
        trace.exception(RuntimeError(f"Unrecognized Field {field_name} in {referenced_group.full_name}"))
        error = error.narrow(Errors.create_field)
        return ..., error
    return output, error.narrow(output.error)
