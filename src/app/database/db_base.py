from sqlalchemy.orm import DeclarativeBase, MappedAsDataclass

class Base(MappedAsDataclass, DeclarativeBase):
    __data_args__ = {"kw_only": True}