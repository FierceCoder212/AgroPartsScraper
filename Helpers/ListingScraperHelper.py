import json
import re
from typing import Optional

import requests


class ListingScraperHelper:
    def __init__(self):
        self.base_url = 'https://www.agroparts.com/ip40_mtdbrand/data/navigation?location={0}&ts=1726069387490'
        self.headers = {
            'cookie': 'IP40SESSIONID=404E8B1D8E4C4E84C8217E2EB6990CD2.PB0; AGROPARTSTOKEN=ppjYiWQwsmbLfmKGaQE3ryDJp4fToveB',
            'host': 'www.agroparts.com'
        }
        self.listing_model_list = []

    def scrape_listing_data(self, location: str = '', model_data: list[str] = None):
        if model_data is None:
            model_data = []
        current_model_data = model_data.copy()
        print(f'Requesting on url : {self.base_url.format(location)}')
        response = requests.get(self.base_url.format(location), headers=self.headers)
        if response.status_code == 200:
            json_response = response.json()
            if 'entries' in json_response:
                entries = json_response['entries']
                current_model_data.append(json_response['label'])
                if any(entry['linkType'] == 'PARTLIST' for entry in entries):
                    self._extract_model(current_model_data, location)
                for entry in entries:
                    if entry['linkType'] == 'MACHINE':
                        new_location = f'{location}/{entry['id']}' if location else entry['id']
                        self.scrape_listing_data(new_location, current_model_data)

    def save_data(self):
        with open('ModelList.json', 'w') as json_file:
            json_file.write(json.dumps(self.listing_model_list, indent=4))

    def _extract_model(self, model_data: list[str], location: str):
        brand, _type, model, model_data = model_data[-4:]
        model_code, year = self._extract_model_data(model_data)
        json_model = {
            'Brand': brand,
            'Type': _type,
            'Model': model,
            'Model Code': model_code,
            'Year': year,
            'Link': f'https://www.agroparts.com/ip40_mtdbrand/#/filtergroup?location={location}'
        }
        print(json.dumps(json_model, indent=4))
        self.listing_model_list.append(json_model)

    @staticmethod
    def _extract_model_data(data: str) -> [Optional[str], Optional[str]]:
        match = re.match(r'([\w-]+)\s+\((\d{4})\)', data)
        if match:
            return match.group(1) if match.group(1) else None, match.group(2) if match.group(2) else None
        return None, None
