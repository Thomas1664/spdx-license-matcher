import codecs
import os
import click
import redis

from spdx_license_matcher.build_licenses import build_spdx_licenses, is_keys_empty,get_url
from spdx_license_matcher.computation import get_close_matches, get_matching_string
from spdx_license_matcher.difference import generate_diff, get_similarity_percent
from spdx_license_matcher.utils import colors, get_spdx_license_text

from dotenv import load_dotenv

load_dotenv()

@click.command()
@click.option('--text_file', '-f', required=True, help='The name of the file in which there is the text you want to match against the SPDX License database.')
@click.option('--threshold', '-t', default=0.9, type = click.FloatRange(0.0, 1.0), help='Confidence threshold below which we just won"t consider it a match.', show_default=True)
@click.option('--build/--no-build', default=False, help='Builds the SPDX license list in the database. If licenses are already present it will update the redis database.')
def matcher(text_file, threshold, build):
    """SPDX License matcher to match license text against the SPDX license list using an algorithm which finds close matches. """
    
    # For python 3
    inputText: str = codecs.open(text_file, 'r', encoding='unicode_escape').read()

    if build or is_keys_empty():
        click.echo('Building SPDX License List. This may take a while...')
        build_spdx_licenses()

    r = redis.StrictRedis(host=os.environ.get(key="SPDX_REDIS_HOST", default="localhost"), port=6379, db=0)
    keys = list(r.keys())
    values = r.mget(keys)
    licenseData = dict(list(zip(keys, values)))
    matches = get_close_matches(inputText, licenseData, threshold)
    matchingString = get_matching_string(matches, inputText)
    if matchingString == '':
        licenseID = max(matches, key=matches.get)
        spdxLicenseText: str = get_spdx_license_text(licenseID)
        ty = type(spdxLicenseText)
        similarityPercent = get_similarity_percent(spdxLicenseText, inputText)
        click.echo(colors('\nThe given license text matches {}% with that of {} based on Levenstein distance.'.format(similarityPercent, licenseID), 94))
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
