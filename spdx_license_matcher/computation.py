from spdx_license_matcher.normalize import normalize
from spdx_license_matcher.sorensen_dice import get_dice_coefficient
from spdx_license_matcher.utils import (checkTextStandardLicense, decompressBytesToString,
                   getListedLicense)

def get_close_matches(inputText: str, licenseData: dict, threshold=0.9):
    """Normalizes the given license text and forms bigrams before comparing it
    with a database of known licenses.

    Arguments:
        text {string} -- text is the license text input by the user.

    Returns:
        dictionary -- dictionary with license name as key and dice coefficient as value.
    """
    matches = {}
    perfectMatches = {}
    normalizedInputText = normalize(inputText)
    for key in list(licenseData.keys()):
        try:
            licenseName = key
            normalizedLicenseText = decompressBytesToString(licenseData.get(key))
        except:
            licenseName = key
            normalizedLicenseText = normalize(licenseData.get(key))
        score = get_dice_coefficient(normalizedInputText, normalizedLicenseText)

        if score == 1.0:
            perfectMatches[licenseName] = score
        else:
            matches[licenseName] = score
    if perfectMatches:
        return perfectMatches
    matches = {licenseName: score for licenseName, score in list(matches.items()) if score >= threshold}
    return matches


def get_matching_string(matches, inputText):
    """Return the matching string with all of the license IDs matched with the input license text if none matches then it returns empty string.
    
    Arguments:
        matches {dictionary} -- Contains the license IDs(which matched with the input text) with their respective sorensen dice score as valus.
        inputText {string} -- license text input by the user.
    
    Returns:
        string -- matching string containing the license IDs that actually matched else returns empty string.
    """
    if not matches:
        matchingString = 'There is not enough confidence threshold for the text to match against the SPDX License database.'
        return matchingString
    
    elif all(score == 1.0 for score in list(matches.values())):
        matchingString = 'The following license ID(s) match: ' + ", ".join(list(matches.keys()))
        return matchingString
    
    else:
        for licenseID in matches:
            listedLicense = getListedLicense(licenseID)
            isTextStandard = checkTextStandardLicense(listedLicense, inputText)
            if not isTextStandard:
                matchingString = 'The following license ID(s) match: ' + licenseID
                return matchingString
        else:
            return ''
