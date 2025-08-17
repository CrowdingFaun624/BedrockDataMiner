from itertools import pairwise
from typing import Required, Sequence

import Utilities.Exceptions as Exceptions
from Component.Dataminer.AbstractDataminerCollectionComponent import (
    AbstractDataminerCollectionComponent,
    AbstractDataminerCollectionTypedDict,
)
from Dataminer.DataminerCollection import DataminerCollection
from Dataminer.DataminerSettings import DataminerSettings
from Utilities.Trace import Trace
from Utilities.TypeVerifier import (
    ListTypeVerifier,
    TypedDictKeyTypeVerifier,
    TypedDictTypeVerifier,
)


class DataminerCollectionTypedDict(AbstractDataminerCollectionTypedDict):
    dataminers: Required[Sequence[DataminerSettings]]

class DataminerCollectionComponent(AbstractDataminerCollectionComponent[DataminerCollection, DataminerCollectionTypedDict]):

    type_name = "DataminerCollection"
    object_type = DataminerCollection
    abstract = False

    type_verifier = AbstractDataminerCollectionComponent.type_verifier.extend(TypedDictTypeVerifier(
        TypedDictKeyTypeVerifier("dataminers", True, ListTypeVerifier(DataminerSettings, list), lambda key, value: (len(value) >= 1, "must not be empty")),
    ))

    def link_final(self, fields: DataminerCollectionTypedDict) -> None:
        super().link_final(fields)
        self.final.link_dataminer_collection(
            dataminer_settings=fields["dataminers"],
        )

    def post_check(self, fields:DataminerCollectionTypedDict, trace:Trace) -> bool:
        last_index = len(fields["dataminers"]) - 1
        error_exists:bool = False
        # ending DataminerSettings must have null versions on corresponding versions; middle ones cannot be null.
        for index, dataminer_settings in enumerate(fields["dataminers"]):
            with trace.enter_key(index, dataminer_settings):
                if index == 0 and dataminer_settings.version_range.stop is not None:
                    trace.exception(Exceptions.ComponentVersionRangeExists(dataminer_settings.version_range.stop, True))
                    error_exists = True
                elif index != 0 and dataminer_settings.version_range.stop is None:
                    trace.exception(Exceptions.ComponentVersionRangeMissing("new"))
                    error_exists = True
                if index == last_index and dataminer_settings.version_range.start is not None:
                    trace.exception(Exceptions.ComponentVersionRangeExists(dataminer_settings.version_range.start, True))
                    error_exists = True
                elif index != last_index and dataminer_settings.version_range.start is None:
                    trace.exception(Exceptions.ComponentVersionRangeMissing("old"))
                    error_exists = True
        if error_exists:
            return True

        for dataminer_settings_new, dataminer_settings_old in pairwise(fields["dataminers"]):
            # checking for None is not necessary because it exists before this if there is, but I must appease the type checker.
            if dataminer_settings_new.version_range.start is not None and dataminer_settings_old.version_range.stop is not None and dataminer_settings_new.version_range.start is not dataminer_settings_old.version_range.stop:
                trace.exception(Exceptions.ComponentVersionRangeGap(dataminer_settings_new.version_range.start, dataminer_settings_old.version_range.stop))
                error_exists = True
        return error_exists
