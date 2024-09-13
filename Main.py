import json

from Helpers.ScraperHelper import ScraperHelper
from Models.ScraperInputModel import ScraperInputModel
from dotenv import load_dotenv, find_dotenv

load_dotenv(find_dotenv('.env'))
with open('ModelData.json', 'r') as model_file:
    data = [ScraperInputModel(**item) for item in json.load(model_file)]
scraper_helper = ScraperHelper(data)
scraper_helper.start_scraper()
