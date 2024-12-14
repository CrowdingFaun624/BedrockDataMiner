import Component.Importer as Importer
import Tablifier.Tablifier as Tablifier
import Utilities.UserInput as UserInput


def select_tablifier(tablifiers:dict[str,Tablifier.Tablifier]) -> Tablifier.Tablifier:
    return UserInput.input_single(tablifiers, "tablifier", show_options_first_time=True, close_enough=True)

def main() -> None:
    tablifiers = Importer.tablifiers
    selected_tablifier = select_tablifier(tablifiers)
    versions = list(Importer.versions.values())
    selected_tablifier.tablify(versions)
