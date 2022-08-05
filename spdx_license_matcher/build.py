from concurrent.futures import ThreadPoolExecutor
import requests
from spdx_license_matcher.db import Database
from spdx_license_matcher.normalize import normalize
from spdx_license_matcher.utils import compressStringToBytes


def get_url(url: str):
    """GET URL and return response"""
    user_agent = 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/51.0.2704.103 Safari/537.36'
    headers = {'User-Agent': user_agent}
    res = requests.get(url, headers=headers)
    return res


def get_licenses(db: Database, table_name: str):
    url = 'https://spdx.org/licenses/licenses.json'

    # Delete all the keys in the current database
    db.create_table(table_name)
    db.clear_table(table_name)

    response = requests.get(url).json()
    licenses = response['licenses']
    licensesUrl = [license.get('detailsUrl') for license in licenses]

    with ThreadPoolExecutor(max_workers=2) as pool:
        responses = list(pool.map(get_url, licensesUrl))

    for response in responses:
        try:
            licenseJson = response.json()
            licenseName = licenseJson['licenseId']
            licenseText = licenseJson['licenseText']

            normalizeText = normalize(licenseText)
            compressedText = compressStringToBytes(normalizeText)

            db.insert(table_name, licenseName, compressedText)
        except Exception as e:
            print(e)
            raise
