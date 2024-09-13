from typing import Optional, List

from pydantic import BaseModel

from Models.ApiRequestModel import ApiRequestModel


class AdditionalPartListInfos(BaseModel):
    availability: Optional[bool]
    dangerousGoodsStatus: Optional[bool]
    emergencyPartStatus: Optional[bool]
    exchangePartStatus: Optional[bool]
    maintenancePartStatus: Optional[bool]
    predecessorPart: Optional[bool]
    serialNumber: Optional[bool]
    successorPart: Optional[bool]
    wearpartStatus: Optional[bool]
    informations: Optional[list[str]]
    picture: Optional[list[str]]


class Hotspot(BaseModel):
    id: Optional[str]
    linkId: Optional[str]
    file: Optional[str]


class Fields(BaseModel):
    position: Optional[str]
    quantity: Optional[str]
    partNumber: Optional[str]
    description: Optional[str]
    remark: Optional[str]
    dimension: Optional[str]
    availability: Optional[str]
    expectedDelivery: Optional[str]

    def to_api_request_model(self, sgl_code: str, section: str, section_diagram_name: str, section_diagram_url: str):
        print(sgl_code, section, self.partNumber, self.description, self.position, section_diagram_name, section_diagram_url)
        return ApiRequestModel(
            id=0,
            sglUniqueModelCode=sgl_code,
            section=section,
            partNumber=self.partNumber if self.partNumber else '',
            description=self.description if self.description else '',
            itemNumber=self.position if self.position else '',
            sectonDiagram=section_diagram_name,
            sectonDiagramUrl=section_diagram_url,
            scraperName='AgroParts'
        )


class Entry(BaseModel):
    id: Optional[str]
    label: Optional[str]
    additionalLabels: Optional[List[str]]
    linkId: Optional[str]
    linkType: Optional[str]
    style: Optional[str]
    purchasable: Optional[bool]
    existsAvailability: Optional[bool]
    existsPartInfo: Optional[bool]
    additionalPartListInfos: Optional[AdditionalPartListInfos]
    attachments: Optional[List[str]]
    hotspots: Optional[List[Hotspot]]
    orderPartNumber: Optional[str]
    orderQuantity: Optional[str]
    extraUseSerials: Optional[str]
    extraUseSerialsText: Optional[str]
    fields: Optional[Fields]


class TableHeader(BaseModel):
    name: Optional[str]
    label: Optional[str]
    type: Optional[str]
    contentBreak: Optional[bool]


class PartListModel(BaseModel):
    id: Optional[str]
    linkType: Optional[str]
    useConstrainedSearch: Optional[bool]
    entries: Optional[List[Entry]]
    attachments: Optional[List[str]]
    tableHeader: Optional[List[TableHeader]]
