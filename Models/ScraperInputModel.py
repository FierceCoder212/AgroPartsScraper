from pydantic import BaseModel


class ScraperInputModel(BaseModel):
    SGL: str
    CatalogLink: str
