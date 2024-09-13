from pydantic import BaseModel


class ApiRequestModel(BaseModel):
    id: int
    sglUniqueModelCode: str
    section: str
    partNumber: str
    description: str
    itemNumber: str
    sectonDiagram: str
    sectonDiagramUrl: str
    scraperName: str
