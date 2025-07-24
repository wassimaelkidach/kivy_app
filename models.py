from sqlalchemy import Column, Integer, Float, String, Text, ForeignKey, LargeBinary
from sqlalchemy.orm import relationship
from database import Base

class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(255))
    telephone = Column(String(15))
    email = Column(String(255), unique=True, index=True)
    password = Column(String(255))

    favoris = relationship("Favori", back_populates="user", cascade="all, delete-orphan")


class Projet(Base):
    __tablename__ = "projets"

    id = Column(Integer, primary_key=True, index=True)
    code_projet = Column(String(100), unique=True, index=True)
    nom_projet = Column(String(255))
    localisation = Column(String(255))
    description = Column(Text)
    images = Column(LargeBinary, nullable=True)
    
    dispos = relationship("Dispo", back_populates="projet")
    favoris = relationship("Favori", back_populates="projet", cascade="all, delete-orphan")


class Dispo(Base):
    __tablename__ = "dispos"

    id = Column(Integer, primary_key=True, index=True)
    code_projet = Column(String(100), ForeignKey("projets.code_projet"))
    type_lg = Column(String(100))
    superfide_min = Column(Float)
    superfide_max = Column(Float)
    prix = Column(Integer)
    nombre_disponible = Column(Integer)

    projet = relationship("Projet", back_populates="dispos")

class Favori(Base):
    __tablename__ = "favoris"

    user_id = Column(Integer, ForeignKey("users.id"), primary_key=True)
    projet_id = Column(Integer, ForeignKey("projets.id"), primary_key=True)

    user = relationship("User", back_populates="favoris")
    projet = relationship("Projet", back_populates="favoris")
