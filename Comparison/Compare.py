from typing import TypeVar

import Comparison.Difference as D

a = TypeVar("a")
Ct1 = TypeVar("Ct1")
Ct2 = TypeVar("Ct2")
Ct3 = TypeVar("Ct3")
Ct4 = TypeVar("Ct4")
def compare(data1:Ct1, data2:Ct2) -> Ct1|Ct2|D.Diff[Ct1,Ct2]:
    '''If both data are dicts, then return a dict with only Diffs.\n
    If both data are lists, then return a list that retains the same indexes, with Diffs where values differ.\n
    If both data are sets, then return a set of Diffs that are only additions or removals.\n
    If data are another type or are different types, then return a Diff.\n'''
    if type(data1) != type(data2):
        return D.Diff(data1, data2)
    elif isinstance(data1, dict) and isinstance(data2, dict):
        return __compare_dict(data1, data2)
    elif isinstance(data1, set) and isinstance(data2, set):
        return __compare_set(data1, data2)
    elif isinstance(data1, list) and isinstance(data2, list):
        return __compare_list(data1, data2)
    else:
        if data1 == data2:
            return data1
        else:
            return D.Diff(data1, data2)

# TODO: make it be able to compare change of keys instead of just change in values.
def __compare_dict(data1:dict[Ct1,Ct2], data2:dict[Ct3,Ct4]) -> dict[Ct1|Ct2|D.Diff[Ct1,Ct2],Ct3|Ct4|D.Diff[Ct3,Ct4]]:
    output:dict[Ct1|Ct2|D.Diff[Ct1,Ct2],Ct3|Ct4|D.Diff[Ct3,Ct4]] = {}
    for key, value in data1.items():
        if key in data2: # key is in both
            if value == data2[key]:
                output[key] = value # add non-differing items to output
            else:
                output[key] = compare(value, data2[key])
        else: # key only in data1
            output[key] = D.Diff(old=value)
    for key, value in data2.items():
        if key in data1: # key is in both; already done
            pass
        else: # key only in data2
            output[key] = D.Diff(new=value)
    return output

def __compare_list(data1:list[Ct1], data2:list[Ct2]) -> list[Ct1|Ct2|D.Diff[Ct1,Ct2]]:
    output:list[Ct1|Ct2|D.Diff[Ct1,Ct2]] = []
    index = 0
    for index, (value1, value2) in enumerate(zip(data1, data2)):
        if value1 == value2:
            output.append(value1) # There are many situations in which you want to retain the identical values, such as in volumes and pitches in sounds.json
        else:
            output.append(compare(value1, value2))
    if len(data1) > len(data2):
        output.extend(D.Diff(old=data1[i]) for i in range(index + 1, len(data1)))
    elif len(data2) > len(data1):
        output.extend(D.Diff(new=data2[i]) for i in range(index + 1, len(data2)))
    else:
        pass
    return output

def __compare_set(data1:set[Ct1], data2:set[Ct2]) -> set[D.Diff[Ct1,Ct2]]:
    output:set[D.Diff] = type(data1)()
    for item in data1:
        if item in data2: # item in both
            output.add(item)
        else: # item is in data1 and not data2
            output.add(D.Diff(old=item))
    for item in data2:
        if item in data1: # item in both (ignore, already done)
            pass
        else:
            output.add(D.Diff(new=item))
    return output
