import json
from typing import Any

def stringify(data:Any) -> str:
    '''Returns the string of data containing no Diffs. Is used in the comparison reporter.'''
    return json.dumps(data)
