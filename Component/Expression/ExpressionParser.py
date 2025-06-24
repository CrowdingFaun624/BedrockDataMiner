from typing import TYPE_CHECKING

from Utilities.Exceptions import NoApplicableExpressionError

if TYPE_CHECKING:
    from Component.Component import Component
    from Component.Expression.Expression import Expression, Reader

def parse_expression(reader:"Reader", source_component:"Component", is_key:bool=False, is_parent:bool=False) -> "Expression":
    '''
    Returns an appropriate Expression from `source`.
    '''
    from Component.Expression.ExpressionTypes import expression_types
    reader_position:int = reader.index
    exceptions:list[Exception] = []
    for expression_type in expression_types:
        reader.set(reader_position)
        try:
            if not expression_type.applicable(reader, is_key):
                continue
        except Exception as e:
            reader.set(reader_position)
            exceptions.append(e)
            continue
        reader.set(reader_position)
        try:
            output = expression_type.parse(reader, source_component, is_key)
            if is_parent and not reader.at_last():
                continue
            return output
        except Exception as e:
            reader.set(reader_position)
            exceptions.append(e)
            continue
    else:
        raise NoApplicableExpressionError(reader) if len(exceptions) == 0 else ExceptionGroup(f"\"{reader.source}\" at {reader.index} cannot be parsed!", exceptions)
