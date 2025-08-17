import Domain.Domain as Domain


class ComponentObject():
    """
    An object created by a Component.

    :param name: The name of the Field that created this object.
    :param full_name: The the name of the Field that created this object, including the Domain and Group.
    :param domain: The Domain this object's Component was created in.
    :param is_inline: If True, this object's Component's Field is contained by another Field.
    """

    __slots__ = (
        "domain",
        "full_name",
        "is_inline",
        "name",
    )

    def __init__(self, name:str, full_name:str, domain:"Domain.Domain", is_inline:bool) -> None:
        self.name = name
        self.full_name = full_name
        self.domain = domain
        self.is_inline = is_inline

    def __repr__(self) -> str:
        return f"<{self.__class__.__name__} {self.full_name}>"

    # NOT hashed; use the default hash. full_name has duplicates.
