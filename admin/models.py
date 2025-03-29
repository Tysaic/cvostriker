from database import Base
from sqlalchemy import Column, Integer, String


class GeneralInfo(Base):
    __tablename__ = 'general_info'

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(32), nullable=False)
    coname = Column(String(32), nullable=False)
    address = Column(String(128), nullable=False)
    country = Column(String(32), nullable=False)
    email = Column(String(32), unique=True, nullable=False)
    phone = Column(String(32), nullable=True)
    short_description = Column(String(256), nullable=True)

    def general_info_as_json(id):
        general_info = GeneralInfo.query.get(id)
        return {
            'id' : id,
            'name': general_info.name,
            'coname': general_info.name,
            'address': general_info.address,
            'country': general_info.country,
            'email': general_info.email,
            'phone': general_info.phone,
            'short_description': general_info.short_description
        }
        
