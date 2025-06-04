import Domain.Domain as Domain
from Tablifier.Tablifier import Tablifier
from Utilities.UserInput import input_single


def select_tablifier(tablifiers:dict[str,Tablifier]) -> Tablifier:
    return input_single(tablifiers, "tablifier", show_options_first_time=True, close_enough=True)

def main(domain:Domain.Domain) -> None:
    tablifiers = domain.tablifiers
    selected_tablifier = select_tablifier(tablifiers)
    versions = list(domain.versions.values())
    selected_tablifier.tablify(versions, domain)
