from typing import Optional

from pydantic import BaseModel


class Entry(BaseModel):
    id: Optional[str]
    label: Optional[str]
    additionalLabels: Optional[list[str]]
    linkId: Optional[str]
    linkType: Optional[str]
    style: Optional[str]
    description: Optional[str]
    imageId: Optional[str]


class PartGroupModel(BaseModel):
    id: Optional[str]
    linkType: Optional[str]
    useConstrainedSearch: Optional[bool]
    entries: Optional[list[Entry]]
    label: Optional[str]
    description: Optional[str]
    thumbnailLabel: Optional[str]
