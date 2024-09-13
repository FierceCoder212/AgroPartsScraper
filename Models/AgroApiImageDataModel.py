from typing import Optional

from pydantic import BaseModel


class ImageModel(BaseModel):
    imageWidth: Optional[int]
    imageHeight: Optional[int]
    imageFormat: Optional[str]
    maxScaleFactor: Optional[float]
    hotspots: Optional[list[dict]]
