from sqlalchemy import create_engine, Column, Integer, String, DateTime, Boolean, ForeignKey
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, relationship
import datetime

Base = declarative_base()

class Student(Base):
    __tablename__ = 'students'
    id        = Column(Integer, primary_key=True)
    name      = Column(String, nullable=False)
    embedding = Column(String, nullable=False)  # we'll store as comma-joined floats

class Attendance(Base):
    __tablename__ = 'attendance'
    id         = Column(Integer, primary_key=True)
    student_id = Column(Integer, ForeignKey('students.id'))
    timestamp  = Column(DateTime, default=datetime.datetime.utcnow)
    present    = Column(Boolean, default=False)
    student    = relationship("Student")

def init_db(uri='sqlite:///faceattend.db'):     #def init_db(uri='postgresql://faceuser:facepass@localhost/faceattend'):
    engine = create_engine(uri)
    Base.metadata.create_all(engine)
    return sessionmaker(bind=engine)