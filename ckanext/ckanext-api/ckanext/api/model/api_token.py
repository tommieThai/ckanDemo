# encoding: utf-8
from __future__ import annotations
from typing import Optional

from sqlalchemy import  Table

from typing_extensions import Self

from ckan.model import meta
from ckan.model import ApiToken as DefaultApiToken

__all__ = [u"ApiToken", u"api_token_table"]


api_token_table = Table(
    u"api_token",
    meta.metadata,
    extend_existing=True
)


class ApiToken(DefaultApiToken):

    @classmethod
    def get_by_name(cls, name: Optional[str], user_id: Optional[str]) -> Optional[Self]:
        if not user_id:
            return None
        q = meta.Session.query(cls).filter(cls.user_id == user_id,cls.name == name ).first()
        return q

meta.mapper(
    ApiToken,
    api_token_table
)