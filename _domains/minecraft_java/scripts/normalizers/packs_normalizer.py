import _domains.minecraft_java.scripts.dataminers.PacksDataminer as PacksDataminer

__all__ = ["packs_normalizer"]


def packs_normalizer(data:list[PacksDataminer.PackTypedDict]) -> list[str]:
    return [pack["name"] for pack in data]
