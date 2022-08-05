# SPDX License Match Tool
A python tool which takes the license text from the user, compares it with the SPDX license list
using an algorithm which finds close matches and returns differences if the input license text is
found to be a close match.

## Installation
* Clone the repository
    * `git clone https://github.com/Thomas1664/spdx-license-match-tool.git`

* Install dependencies
    * `pip3 install -r requirements.txt`
 
*The SQLite database that is built into Python is used to store the license text of license present on the SPDX license list. For the very first time it may take a while to save the licenses on the database.*

*SPDX License Matcher matches the license text input by the user (via license submittal form) against the data present on the database to find full and near matches.*


## Usage
To run the tool just use the command `python matcher.py -f <file-name> -t <threshold>`.
* `filename` is the file with the license text (if you don't provide the file as well then it will prompt you to add it).
* `threshold` is a value upto which we will just won't consider a match. (optional)

You can also run `python matcher.py --help` for more info.


## Workflow
The workflow of the tool is as follows:
* Reads the license text as input from the user.
* Build a redis database with all the license text present on the SPDX license list.
* Compare the license text with the license text present in the database.
    * Normalises the license text based on the SPDX Matching guidelines while ignore the replaceable text
    and only focusing on substantial text for matching purposes.
    * Tokenizes normalised text into a list of bigrams. This is necessary for the token based algorithm we are using for our use case.
    * Use a token based similarity metric algorithm namely [Sorensen dice algorithm](https://en.wikipedia.org/wiki/S%C3%B8rensen%E2%80%93Dice_coefficient) which is based on the logic to find the common tokens, and divide it by the total number of tokens present by combining both of the sets. This algorithm helps us to distinguish our close matches.
    * A threshold value is used where we just won't consider a match.
    * If the match is 100% then we say it is a perfect match.
    * If the match is between a threshold value and 100% then we apply the full matching algorithms and compares the closely matched license text to the license text of SPDX Standard License using a [method](https://github.com/spdx/tools/blob/b61e655ad997d7669faab65cff7d0b36da03cab5/src/org/spdx/compare/LicenseCompareHelper.java#L568) present in the SPDX Java-based tools. 
        * If there is a match then the given license text matches with the SPDX standard license.
        * If there is no match then we simply display the differences of the given license text with that of SPDX license list.
