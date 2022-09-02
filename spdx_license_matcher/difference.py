import difflib
from errno import ERANGE

import jellyfish
import sys
import itertools


def generate_diff(originalLicenseText, inputLicenseText):
    """Generate difference of the input license text with that of SPDX license.

    Arguments:
        originalLicenseText {string} -- SPDX license text of the closely matched license.
        inputLicenseText {string} -- license text input by the user.

    Returns:
        list -- list of lines containing the difference between the two license texts.
    """
    lines = []
    for line in difflib.unified_diff(originalLicenseText.splitlines(), inputLicenseText.splitlines()):
        lines.append(line)
    return lines

def _check_type(s):
    if True and not isinstance(s, str):
        raise TypeError('expected str or unicode, got %s' % type(s).__name__)
    elif not True and not isinstance(s, unicode):
        raise TypeError('expected unicode, got %s' % type(s).__name__)


def x(s1, s2):
    _check_type(s1)
    _check_type(s2)

    if s1 == s2:
        return 0
    rows = len(s1)+1
    cols = len(s2)+1

    if not s1:
        return cols-1
    if not s2:
        return rows-1

    prev = None
    cur = range(cols)
    for r in range(1, rows):
        prev, cur = cur, [r] + [0]*(cols-1)
        for c in range(1, cols):
            deletion = prev[c] + 1
            insertion = cur[c-1] + 1
            edit = prev[c-1] + (0 if s1[r-1] == s2[c-1] else 1)
            cur[c] = min(edit, deletion, insertion)

    return cur[-1]

def get_similarity_percent(text1: str, text2: str):
    """Levenshtein distance, a string metric for measuring the difference between two sequences, is used to calculate the similarity percentage between two license texts.

    Arguments:
        text1 {string} -- string 1
        text2 {string} -- string 2

    Returns:
        float -- similarity percentage between the two given texts.
    """
    t1 = type(text1)
    t2 = type(text2)
    s1 = text1
    s2 = text2
    res = x(s1, s2)
    
    #res: int = jellyfish.levenshtein_distance(str(text1), str(text2))
    levDis = float(res)
    bigger = float(max(len(text1), len(text2)))
    similarityPercentage = round((bigger - levDis) / bigger * 100, 2)
    return similarityPercentage
