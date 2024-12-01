import Component.Importer as Importer
import Tablifier.Tablifier as Tablifier


def select_tablifier(tablifiers:dict[str,Tablifier.Tablifier]) -> Tablifier.Tablifier:
    user_input = None
    while user_input not in tablifiers:
        user_input = input("Select a Tablifier from [%s]: " % (", ".join("\"%s\"" % (tablifier_name,) for tablifier_name in tablifiers),))
    return tablifiers[user_input]

def main() -> None:
    tablifiers = Importer.tablifiers
    selected_tablifier = select_tablifier(tablifiers)
    versions = list(Importer.versions.values())
    selected_tablifier.tablify(versions)
