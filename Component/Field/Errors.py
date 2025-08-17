from enum import IntEnum
from typing import Iterable


class Errors(IntEnum):
    """
    Items of this Enum describe the first step this Field cannot complete.
    """
    create_field = 0
    create_final = 1
    link_final = 2
    finalize = 3
    returning = 4
    fine = 5
    """
    There is no error with this Field.
    """

    def narrow(self, other:"Errors") -> "Errors":
        """
        Returns the earlier of the two options.
        """
        return min(self, other)

    def narrows(self, others:Iterable["Errors"]) -> "Errors":
        """
        Returns the narrow of all of the options, including self.
        """
        return min(self, min(others))
