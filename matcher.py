import codecs
import imp
import click
from dotenv import load_dotenv

from spdx_license_matcher.db import Database
from spdx_license_matcher.build import *
from spdx_license_matcher.computation import get_close_matches, get_matching_string
from spdx_license_matcher.difference import generate_diff, get_similarity_percent
from spdx_license_matcher.utils import colors, decompressBytesToString, get_spdx_license_text

load_dotenv()

@click.command()
@click.option('--text_file', '-f', required=True, help='The name of the file in which there is the text you want to match against the SPDX License database.')
@click.option('--threshold', '-t', default=0.9, type = click.FloatRange(0.0, 1.0), help='Confidence threshold below which we just won"t consider it a match.', show_default=True)
@click.option('--build/--no-build', default=False, help='Builds the SPDX license list in the database. If licenses are already present it will update the redis database.')
def matcher(text_file, threshold, build):
    """SPDX License matcher to match license text against the SPDX license list using an algorithm which finds close matches. """
    
    # For python 3
    inputText: str = codecs.open(text_file, 'r', encoding='unicode_escape').read()

    # Database constants
    db_file = 'licenses.db'
    table_name = 'license'
    db = Database(db_file, table_name)

    if build or db.is_table_empty(table_name):
        click.echo('Building SPDX License List. This may take a while...')
        get_licenses(db, table_name)

    res = db.select_all(table_name)
    keys, values = zip(*res)

    licenseData = dict(list(zip(keys, values)))
    matches = get_close_matches(inputText, licenseData, threshold)
    matchingString = get_matching_string(matches, inputText)
    
    if matchingString == '':
        licenseID = max(matches, key=matches.get)
        spdxLicenseText: str = get_spdx_license_text(licenseID)
        ty = type(spdxLicenseText)
        similarityPercent = get_similarity_percent(spdxLicenseText, inputText)
        click.echo(colors('\n License: {} ({}% match)'.format(licenseID, similarityPercent), 94))
        if False:
            differences = generate_diff(spdxLicenseText, inputText)
            for line in differences:
                if line[0] == '+':
                    line = colors(line, 92)
                if line[0] == '-':
                    line = colors(line, 91)
                if line[0] == '@':
                    line = colors(line, 90)
                click.echo(line)
    else:
        click.echo(colors(matchingString, 92))


if __name__ == "__main__":
    matcher()
