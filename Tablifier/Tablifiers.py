import Domain.Domain as Domain
import Tablifier.Tablifier as Tablifier
import Utilities.UserInput as UserInput


def select_tablifier(tablifiers:dict[str,Tablifier.Tablifier]) -> Tablifier.Tablifier:
    return UserInput.input_single(tablifiers, "tablifier", show_options_first_time=True, close_enough=True)

def main(domain:Domain.Domain) -> None:
    tablifiers = domain.tablifiers
    selected_tablifier = select_tablifier(tablifiers)
    versions = list(domain.versions.values())
    selected_tablifier.tablify(versions)
