import Comparison.Comparer as Comparer

comparer = Comparer.Comparer(
    normalizer=None,
    dependencies=None,
    base_comparer_section=Comparer.ListComparerSection(
        name="sound event",
        types=(str,),
        measure_length=True,
        ordered=False,
        comparer=None,
    )
)
