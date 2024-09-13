import json
import re
from typing import Optional

import requests

from Helpers.MSSQLHelper import MSSqlHelper
from Models.AgroApiImageDataModel import ImageModel
from Models.AgroApiPartGroupModel import PartGroupModel, Entry
from Models.AgroApiResponseModel import PartListModel
from Models.ScraperInputModel import ScraperInputModel


class ScraperHelper:
    def __init__(self, input_model: list[ScraperInputModel]):
        self.input_model: list[ScraperInputModel] = input_model
        self.base_url = 'https://www.agroparts.com/ip40_mtdbrand/data/navigation?location={0}&ts=1726167159713'
        self.img_data_base_url = 'https://www.agroparts.com/ip40_mtdbrand/imagedata?path={0}&request=GetImageInfo&cv=1'
        self.base_img_url = 'https://www.agroparts.com/ip40_mtdbrand/imagedata?path={0}&request=GetImage&format={1}&bbox=0,0,{2},{3}&width={2}&height={3}&scalefac={4}&ticket=&cv=1'
        self.sql_helper = MSSqlHelper()
        self.images = []
        self.headers = {
            "accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.7",
            "accept-encoding": "gzip, deflate, br, zstd",
            "accept-language": "en-GB,en-US;q=0.9,en;q=0.8",
            "cache-control": "max-age=0",
            "cookie": "IP40SESSIONID=B239CF0934A4676446D9DD5736070CBB.PB0; AGROPARTSTOKEN=i4iYA4t5__-rcS37Ak-QEBE-E3bzyheF",
            "priority": "u=0, i",
            "sec-ch-ua": '"Chromium";v="128", "Not;A=Brand";v="24", "Google Chrome";v="128"',
            "sec-ch-ua-mobile": "?0",
            "sec-ch-ua-platform": '"Windows"',
            "sec-fetch-dest": "document",
            "sec-fetch-mode": "navigate",
            "sec-fetch-site": "none",
            "sec-fetch-user": "?1",
            "upgrade-insecure-requests": "1",
            "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/128.0.0.0 Safari/537.36"
        }

    def start_scraper(self):
        for index, item in enumerate(self.input_model):
            print(f'On item-{index + 1} of {len(self.input_model)}')
            url, location = self._get_catalog_api_link(item)
            response = requests.get(url, headers=self.headers)
            if response.status_code == 200:
                part_group_model = PartGroupModel(**response.json())
                for category_index, category in enumerate(part_group_model.entries):
                    print(f'On item-{index + 1} of {len(self.input_model)}, Category-{category_index + 1} of {len(part_group_model.entries)}')
                    api_request_models = self._extract_parts_from_category(category=category, location=location, item=item)
                    print(f'Saving models: {len(api_request_models)}')
                    self.sql_helper.insert_many_records(api_request_models)
        with open('ImagesData.json', 'w') as json_file:
            json_file.write(json.dumps(self.images, indent=4))
        print('All items scraped successfully...')

    def _extract_parts_from_category(self, category: Entry, location: str, item: ScraperInputModel) -> list[dict]:
        response = requests.get(self.base_url.format('/'.join([location, category.id])), headers=self.headers)
        if response.status_code == 200:
            return self._parts_to_api_request_model(item=item, category=category, parts_list=PartListModel(**response.json()).entries)
        return []

    def _get_catalog_api_link(self, item: ScraperInputModel) -> [str, str]:
        location = item.CatalogLink.replace('https://www.agroparts.com/ip40_mtdbrand/#/filtergroup?location=', '')
        return self.base_url.format(location), location

    def _parts_to_api_request_model(self, item: ScraperInputModel, category: Entry, parts_list: list[Entry]) -> list[dict]:
        img_url = self._get_img_url(parts_list)
        img_file_name = self._sanitize_filename(f'{item.SGL}-{category.label}.jpg')
        self.images.append({
            'FileName': img_file_name,
            'ImgUrl': img_url
        })
        return [part.fields.to_api_request_model(sgl_code=item.SGL, section=category.label, section_diagram_name=img_file_name, section_diagram_url=img_url).model_dump() for part in parts_list]

    @staticmethod
    def _get_img_link_id(parts_list: list[Entry]) -> Optional[str]:
        for entry in parts_list:
            if entry.hotspots:
                return entry.hotspots[0].linkId
        return None

    def _get_img_url(self, parts_list: list[Entry]) -> str:
        if img_link_id := self._get_img_link_id(parts_list):
            response = requests.get(self.img_data_base_url.format(img_link_id), headers=self.headers)
            if response.status_code == 200:
                image_data_model = ImageModel(**response.json())
                return self.base_img_url.format(img_link_id, image_data_model.imageFormat, image_data_model.imageWidth, image_data_model.imageHeight, image_data_model.maxScaleFactor)
        return ''

    @staticmethod
    def _sanitize_filename(filename: str) -> str:
        """
        Convert invalid filenames to valid filenames by replacing or removing invalid characters.
        """
        invalid_chars = r'[<>:"/\\|?*\']'
        sanitized_filename = re.sub(invalid_chars, "_", filename)
        sanitized_filename = sanitized_filename.strip()
        sanitized_filename = sanitized_filename[:255]
        return sanitized_filename
