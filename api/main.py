# main.py
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from sqlalchemy import create_engine, Column, Integer, Float, String, Boolean, Date, ForeignKey, Sequence
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship, sessionmaker
from dotenv import load_dotenv
import os
import datetime
import random  # Placeholder for the actual model inference

# Load environment variables from .env file
load_dotenv()

# Database connection parameters from environment variables
host = os.getenv('DB_HOST')
port = os.getenv('DB_PORT')
dbname = os.getenv('DB_NAME')
user = os.getenv('DB_USER')
password = os.getenv('DB_PASSWORD')

# Create the database URL
DATABASE_URL = f'postgresql+pg8000://{user}:{password}@{host}:{port}/{dbname}'

# Create the engine
engine = create_engine(DATABASE_URL, echo=True)

# Base class for declarative models
Base = declarative_base()

# Define the tables
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
    power_value = Column(Float, nullable=False)
    date_logged = Column(Date, nullable=False)
    
    user = relationship('PowerMeter', back_populates='recent_power_values')

class AnomalyPredictions(Base):
    __tablename__ = 'anomaly_predictions'
    id = Column(Integer, Sequence('anomaly_predictions_id_seq'), primary_key=True, autoincrement=True)
    user_id = Column(Integer, ForeignKey('power_meter.user_id'), nullable=False)
    anomaly = Column(Boolean, nullable=False)
    date_predicted = Column(Date, nullable=False)
    
    user = relationship('PowerMeter', back_populates='anomaly_predictions')

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

app = FastAPI()

class PowerValueInput(BaseModel):
    user_id: int
    power_value: float

class PredictionOutput(BaseModel):
    user_id: int
    anomaly: bool
    date_predicted: datetime.date

def perform_inference(values):
    # This should be replaced with actual model inference logic
    return random.choice([True, False])

@app.post("/add_power_value/", response_model=PredictionOutput)
def add_power_value(input: PowerValueInput):
    session = SessionLocal()
    try:
        new_power_value = PowerValues(
            user_id=input.user_id,
            power_value=input.power_value,
            date_logged=datetime.date.today()
        )
        session.add(new_power_value)
        session.commit()
        
        recent_values = session.query(RecentPowerValues).filter_by(user_id=input.user_id).order_by(RecentPowerValues.date_logged.desc()).limit(25).all()
        recent_values_list = [rv.power_value for rv in recent_values]
        
        recent_values_list.append(input.power_value)
        
        anomaly = perform_inference(recent_values_list)
        
        new_prediction = AnomalyPredictions(
            user_id=input.user_id,
            anomaly=anomaly,
            date_predicted=datetime.date.today()
        )
        session.add(new_prediction)
        session.commit()
        
        session.query(RecentPowerValues).filter_by(user_id=input.user_id).delete()
        for power_value in recent_values_list[-25:]:
            recent_power_value = RecentPowerValues(
                user_id=input.user_id,
                power_value=power_value,
                date_logged=datetime.date.today()
            )
            session.add(recent_power_value)
        session.commit()
        
        return PredictionOutput(user_id=input.user_id, anomaly=anomaly, date_predicted=datetime.date.today())
    
    except Exception as e:
        session.rollback()
        raise HTTPException(status_code=400, detail=str(e))
    
    finally:
        session.close()
