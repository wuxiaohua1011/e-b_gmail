from pydantic import BaseModel
from typing import List, Dict, Union
import base64


class EmailMeta(BaseModel):
    id: str
    threadId: str


class Body(BaseModel):
    attachmentId: Union[str, None]
    data: Union[str, None]
    size: int

    @classmethod
    def decodeMessage(cls, message):
        return base64.b64decode(message)


class Header(BaseModel):
    name: str
    value: str


class PartBody(BaseModel):
    size: int
    data: str

    @classmethod
    def decodeMessage(cls, message):
        return base64.urlsafe_b64decode(message)


class Part(BaseModel):
    partId: str
    mimeType: str
    filename: str
    headers: List
    body: PartBody


class Payload(BaseModel):
    body: Body
    filename: str
    headers: List[Header]
    mimeType: str
    partId: str
    parts: List[Part]


class Email(BaseModel):
    historyId: str
    id: str
    internalDate: str
    labelIds: List[str]
    payload: Payload
    raw: Union[str, None]
    sizeEstimate: int
    snippet: str
    threadId: str

    def decode_email(self):
        for part in self.payload.parts:
            part.body.data = PartBody.decodeMessage(part.body.data)
