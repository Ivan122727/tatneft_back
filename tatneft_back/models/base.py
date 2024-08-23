from __future__ import annotations

from datetime import datetime
from ipaddress import IPv4Interface, IPv4Address
from typing import Any, Optional

from bson import ObjectId
from pydantic import BaseModel, Field, Extra
from pydantic.fields import ModelField

from tatneft_back.db.collections.base import BaseFields, Document


class BaseDBM(BaseModel):
    misc_data: dict[Any, Any] = Field(default={})
    
    # db fields
    oid: Optional[ObjectId] = Field(alias=BaseFields.oid)
    int_id: Optional[int] = Field(alias=BaseFields.int_id)
    created: Optional[datetime] = Field(alias=BaseFields.created)

    class Config:
        extra = Extra.ignore
        arbitrary_types_allowed = True
        allow_population_by_field_name = True

        json_encoders = {
            ObjectId: str,
            datetime: lambda v: v.timestamp()
        }

    def to_json(self, **kwargs) -> str:
        kwargs["indent"] = 2
        kwargs["ensure_ascii"] = False
        return self.json(**kwargs)

    def to_dict(self, only_db_fields: bool = True, **kwargs) -> dict:
        data = self.dict(**kwargs)
        if only_db_fields is True:
            for f in self.__fields__.values():
                f: ModelField
                if f.alias not in data:
                    continue
                if f.has_alias is False:
                    del data[f.alias]
                    continue
        return data

    @classmethod
    def parse_document(cls, doc: Document) -> BaseDBM:
        """get only fields that has alias and exists in doc"""
        doc_to_parse = {}
        for f in cls.__fields__.values():
            f: ModelField
            if f.has_alias is False:
                continue
            if f.alias not in doc:
                continue
            doc_to_parse[f.alias] = doc[f.alias]
        return cls.parse_obj(doc_to_parse)

    def document(self) -> Document:
        doc = self.dict(by_alias=True, exclude_none=False, exclude_unset=False, exclude_defaults=False)
        for f in self.__fields__.values():
            f: ModelField
            if f.alias not in doc:
                continue
            if f.has_alias is False:
                del doc[f.alias]
                continue
            if doc[f.alias] is None:
                continue
            if f.outer_type_ in [IPv4Interface, IPv4Address]:
                doc[f.alias] = str(doc[f.alias])
            elif f.outer_type_ in [list[IPv4Interface], list[IPv4Address]]:
                doc[f.alias] = [str(ip) for ip in doc[f.alias]]
        return doc