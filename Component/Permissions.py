import enum


class InlinePermissions(enum.Enum):
    "Applied to a Component to determine how it may be referenced by other Components."

    inline = 0
    "Inline Components are allowed."
    mixed = 1
    "Both inline and reference Components are allowed."
    reference = 2
    "Only reference Components are allowed. Includes reference inheritance."
    none = 3
    "This Component cannot be referenced or created inline"

class InheritancePermissions(enum.Enum):
    """
    Applied to a Component to determine how it may use inheritance.
    If inline Components are not allowed, regular inheritance is not allowed
    but reference inheritance is.
    """

    regular_inheritance = 0
    "Only normal usage and regular inheritance are allowed."
    mixed = 1
    "Both normal usage, reference inheritance, and regular inheritance are allowed."
    reference_inheritance = 2
    "Only normal usage and reference inheritance are allowed."
    normal = 3
    "Only normal usage is allowed."

class InlineUsage(enum.Enum):
    "Used by Field.choose_component to specify if a Component is referenced or inline."

    inline = "inline"
    reference = "reference"
    unknown = "unknown"
    "Used if an error has occurred when referencing the Component"

class InheritanceUsage(enum.Enum):
    """
    Used by Field.choose_component to specify if a Component is referenced
    using reference inheritance, regular inheritance, or neither.
    """

    normal = "normal"
    regular_inheritance = "regular inheritance"
    reference_inheritance = "reference inheritance"
    unknown = "unknown"
    "Used if an error has occurred when referencing the Component"
