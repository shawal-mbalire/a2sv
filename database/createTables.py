from sqlalchemy import create_engine, Column, Integer, String, Float, Boolean, Date, ForeignKey, Sequence
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship, sessionmaker
from dotenv import load_dotenv
import os

load_dotenv()

host = os.getenv('DB_HOST')
port = os.getenv('DB_PORT')
dbname = os.getenv('DB_NAME')
user = os.getenv('DB_USER')
password = os.getenv('DB_PASSWORD')

DATABASE_URL = f'postgresql+pg8000://{user}:{password}@{host}:{port}/{dbname}'
engine = create_engine(DATABASE_URL, echo=True)
Base = declarative_base()

class PowerMeter(Base):
    __tablename__ = 'power_meter'
    user_id = Column(Integer, Sequence('user_id_seq'), primary_key=True, autoincrement=True)
    location_longitude = Column(Float, nullable=False)
    location_latitude = Column(Float, nullable=False)
    district = Column(String(100), nullable=False)
    region = Column(String(100), nullable=False)
    
    power_values = relationship('PowerValues', back_populates='user')
    recent_power_values = relationship('RecentPowerValues', back_populates='user')
    anomaly_predictions = relationship('AnomalyPredictions', back_populates='user')

class PowerValues(Base):
    __tablename__ = 'power_values'
    id = Column(Integer, Sequence('power_values_id_seq'), primary_key=True, autoincrement=True)
    user_id = Column(Integer, ForeignKey('power_meter.user_id'), nullable=False)
    power_value = Column(Float, nullable=False)
    date_logged = Column(Date, nullable=False)
    
    user = relationship('PowerMeter', back_populates='power_values')

class RecentPowerValues(Base):
    __tablename__ = 'recent_power_values'
    id = Column(Integer, Sequence('recent_power_values_id_seq'), primary_key=True, autoincrement=True)
    user_id = Column(Integer, ForeignKey('power_meter.user_id'), nullable=False)
    power_value = Column(String, nullable=False)
    date_logged = Column(Date, nullable=False)
    
    user = relationship('PowerMeter', back_populates='recent_power_values')

class AnomalyPredictions(Base):
    __tablename__ = 'anomaly_predictions'
    id = Column(Integer, Sequence('anomaly_predictions_id_seq'), primary_key=True, autoincrement=True)
    user_id = Column(Integer, ForeignKey('power_meter.user_id'), nullable=False)
    anomaly = Column(Boolean, nullable=False)
    date_predicted = Column(Date, nullable=False)
    
    user = relationship('PowerMeter', back_populates='anomaly_predictions')

Base.metadata.create_all(engine)
