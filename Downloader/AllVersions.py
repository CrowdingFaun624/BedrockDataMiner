import Downloader.VersionsParser as VersionsParser

def main() -> None:
    versions = list(reversed(VersionsParser.parse()))
    print([version.name for version in versions])
