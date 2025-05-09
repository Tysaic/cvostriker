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
    user_id = Column(Integer, ForeignKey('user.id'), unique=True, nullable=False)
    user = relationship("User", back_populates="general_info")

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

    user_id = Column(Integer, ForeignKey('user.id'), nullable=False)
    user = relationship("User", back_populates='multimedias')
    

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

    
    user_id = Column(Integer, ForeignKey('user.id'), nullable=False)
    user = relationship("User", back_populates='experiences')

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

    
    user_id = Column(Integer, ForeignKey('user.id'), nullable=False)
    user = relationship("User", back_populates='certifications')

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

class Projects(Base):

    __tablename__ = 'projects'

    id = Column(Integer, primary_key=True, index=True)
    title = Column(String(128), nullable=False)
    description = Column(Text, nullable=False)
    init_date = Column(DateTime, nullable=False)
    end_date = Column(DateTime, nullable=True)
    aptitudes = Column(Text, nullable=False)

    user_id = Column(Integer, ForeignKey('user.id'), nullable=False)
    user = relationship("User", back_populates='projects')

    @staticmethod
    def projects_as_json(session, id:int):
        projects = session.query(Projects).get(id)

        if not projects:
            return jsonify({'error': 'There are not projects existings'}), 404
        
        else:
            return jsonify({
                'id': projects.id,
                'title': projects.title,
                'description': projects.description,
                'init_date': projects.init_date,
                'end_date': projects.end_date,
                'aptitudes': projects.aptitudes
            })

class Configuration(Base):

    __tablename__ = 'configuration'
    
    id = Column(Integer, primary_key=True, index=True)
    theme = Column(String(32), nullable=False, default='light')
    language = Column(String(32), nullable=False, default='en')
    font_size = Column(String(32), nullable=False, default='medium')
    OTP = Column(String(32), nullable=True)
    # OTP is a one-time password for two-factor authentication

    user_id = Column(Integer, ForeignKey('user.id'), unique=True, nullable=False)
    user = relationship("User", back_populates="configuration")
    # Allowed values for fields
    THEMES = ['light', 'dark', 'blue']
    LANGUAGES = ['en', 'es', 'fr', 'de']
    FONT_SIZES = ['small', 'medium', 'large']


class User(Base):

    __tablename__ = 'user'
    id = Column(Integer, primary_key=True, index=True)
    username = Column(String(32), unique=True, nullable=False)
    password = Column(String(128), nullable=False)
    # uselist=False means that this relationship is one-to-one and get the object directly e.g: user.general_info
    general_info = relationship("GeneralInfo", back_populates="user", uselist=False, cascade="all, delete-orphan")
    configuration = relationship("Configuration", back_populates="user", uselist=False, cascade="all, delete-orphan")

    # uselist=True means that this relationship is one-to-many and get the list of objects e.g: user.multimedias
    multimedias = relationship("Multimedia", back_populates="user", cascade="all, delete-orphan")
    experiences = relationship("Experience", back_populates="user", cascade="all, delete-orphan")
    certifications = relationship("Certification", back_populates="user", cascade="all, delete-orphan")
    projects = relationship("Projects", back_populates="user", cascade="all, delete-orphan")