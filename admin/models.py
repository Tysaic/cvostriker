from database import Base
from sqlalchemy import Column, Integer, String, DateTime, ForeignKey, Text
from sqlalchemy.orm import relationship
from flask import jsonify
import datetime


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

    @staticmethod
    def general_info_as_json(session, id: int):
        general_info = session.query(GeneralInfo).get(id)
        return jsonify({
            'id' : id,
            'name': general_info.name,
            'coname': general_info.name,
            'address': general_info.address,
            'country': general_info.country,
            'email': general_info.email,
            'phone': general_info.phone,
            'short_description': general_info.short_description
        }), 200



class Multimedia(Base):

    __tablename__ = 'multimedia'

    id = Column(Integer, primary_key=True, index=True)
    filename = Column(String(128), nullable=False)
    file_type = Column(String(32), nullable=False)
    created_at = Column(DateTime, nullable=False)

    @staticmethod
    def multimedia_as_json(session, id: int):
        multimedia = session.query(Multimedia).get(id)
        
        if not multimedia:
            return jsonify({'error': 'Multimedia not found'}), 404

        return jsonify({
            'id': id,
            'filename': multimedia.filename,
            'file_type': multimedia.file_type,
            'created_at': multimedia.created_at
        }), 200


class Experience(Base):

    __tablename__ = 'experience'

    id = Column(Integer, primary_key=True, index=True)
    short_description = Column(String(256), nullable=False)
    company = Column(String(32), nullable=False)
    position = Column(String(32), nullable=False)
    location = Column(String(32), nullable=False)
    long_description = Column(Text, nullable=False)
    aptitudes = Column(Text, nullable=False)
    start_date = Column(DateTime, nullable=False)
    end_date = Column(DateTime, nullable=True)

    @staticmethod
    def experience_as_json(session, id: int):
        experience = session.query(Experience).get(id)

        if not experience:
            return jsonify({'error': 'Experience not found'}), 404
        else:
            return jsonify({
                'id': id,
                'short_description': experience.short_description,
                'long_description': experience.long_description,
                'company': experience.company,
                'position': experience.position,
                'location': experience.location,
                'start_date': experience.start_date,
                'end_date': experience.end_date,
                'aptitudes': experience.aptitudes,
            })

class Certification(Base):

    __tablename__ = 'certification'

    id = Column(Integer, primary_key=True, index=True)
    title = Column(String(128), nullable=False)
    description = Column(Text, nullable=False)
    filename = Column(String(64), nullable=False)
    file_type = Column(String(8), nullable=False)
    upload_at = Column(DateTime, nullable=False, default=datetime.datetime.now)

    @staticmethod
    def certification_as_json(session, id:int):
        certification = session.query(Certification).get(id)

        if not certification:
            return jsonify({'error': 'Certification not found'}), 404
        else:
            return jsonify({
                'id': certification.id,
                'title': certification.title,
                'description': certification.description,
                'filename': certification.filename,
                'file_type': certification.file_type,
                'upload_at': certification.upload_at
            })