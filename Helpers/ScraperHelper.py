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

    def start_scraper(self):
        for index, item in enumerate(self.input_model):
            print(f'On item-{index + 1} of {len(self.input_model)}')
            url, location = self._get_catalog_api_link(item)
            response = requests.get(url)
            if response.status_code == 200:
                part_group_model = PartGroupModel(**response.json())
                for category_index, category in enumerate(part_group_model.entries):
                    print(f'On item-{index + 1} of {len(self.input_model)}, Category-{category_index + 1} of {len(part_group_model.entries)}')
                    api_request_models = self._extract_parts_from_category(category=category, location=location, item=item)
                    print(f'Saving models: {len(api_request_models)}')
                    self.sql_helper.insert_many_records(api_request_models)
                    break
            break
        with open('ImagesData.json', 'w') as json_file:
            json_file.write(json.dumps(self.images, indent=4))
        print('All items scraped successfully...')

    def _extract_parts_from_category(self, category: Entry, location: str, item: ScraperInputModel) -> list[dict]:
        response = requests.get(self.base_url.format('/'.join([location, category.id])))
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
            response = requests.get(self.img_data_base_url.format(img_link_id))
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
