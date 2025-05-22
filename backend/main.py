from fastapi import FastAPI, Depends, HTTPException
from sqlalchemy import create_engine, select
from sqlalchemy.orm import sessionmaker, Session
from sqlalchemy.ext.declarative import declarative_base
from typing import List # Import List

from . import models # Import models
from .models import ValueStreamMapCreate, ValueStreamMap as ValueStreamMapResponse, VSMStepCreate # Import Pydantic schemas and SQLAlchemy models

DATABASE_URL = "sqlite:///./vsm.db"

engine = create_engine(DATABASE_URL, connect_args={"check_same_thread": False})
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base() # This should be models.Base from models.py

app = FastAPI()

# Dependency for DB Session
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

# Create database tables - This should use models.Base
# Ensure models are imported before this line or Base is defined in main.py and used by models.py
models.Base.metadata.create_all(bind=engine) # Corrected to use models.Base

# API Endpoints

# POST /api/vsm (Create VSM)
@app.post("/api/vsm", response_model=ValueStreamMapResponse, status_code=201)
def create_vsm(vsm_create: ValueStreamMapCreate, db: Session = Depends(get_db)):
    db_vsm = models.ValueStreamMap(title=vsm_create.title)
    db.add(db_vsm)
    db.flush() # Use flush to get the ID for the steps

    for step_data in vsm_create.steps:
        db_step = models.VSMStep(**step_data.dict(), map_id=db_vsm.id)
        db.add(db_step)
    
    db.commit()
    db.refresh(db_vsm) # Refresh to get the steps loaded
    return db_vsm

# GET /api/vsm (List VSMs)
@app.get("/api/vsm", response_model=List[ValueStreamMapResponse])
def list_vsms(db: Session = Depends(get_db)):
    vsms = db.execute(select(models.ValueStreamMap)).scalars().all()
    return vsms

# GET /api/vsm/{vsm_id} (Retrieve VSM)
@app.get("/api/vsm/{vsm_id}", response_model=ValueStreamMapResponse)
def retrieve_vsm(vsm_id: int, db: Session = Depends(get_db)):
    vsm = db.get(models.ValueStreamMap, vsm_id) # Simpler way to get by PK
    if not vsm:
        raise HTTPException(status_code=404, detail="ValueStreamMap not found")
    return vsm

# PUT /api/vsm/{vsm_id} (Update VSM)
@app.put("/api/vsm/{vsm_id}", response_model=ValueStreamMapResponse)
def update_vsm(vsm_id: int, vsm_update: ValueStreamMapCreate, db: Session = Depends(get_db)):
    db_vsm = db.get(models.ValueStreamMap, vsm_id)
    if not db_vsm:
        raise HTTPException(status_code=404, detail="ValueStreamMap not found")

    # Update title
    db_vsm.title = vsm_update.title
    
    # Delete existing steps
    for step in db_vsm.steps:
        db.delete(step)
    db.flush() # Ensure deletes are processed before adding new ones

    # Create new steps
    for step_data in vsm_update.steps:
        db_step = models.VSMStep(**step_data.dict(), map_id=db_vsm.id)
        db.add(db_step)
        
    db.commit()
    db.refresh(db_vsm)
    return db_vsm

# DELETE /api/vsm/{vsm_id} (Delete VSM)
@app.delete("/api/vsm/{vsm_id}", status_code=204)
def delete_vsm(vsm_id: int, db: Session = Depends(get_db)):
    db_vsm = db.get(models.ValueStreamMap, vsm_id)
    if not db_vsm:
        raise HTTPException(status_code=404, detail="ValueStreamMap not found")
    
    db.delete(db_vsm)
    db.commit()
    return # FastAPI will return 204 No Content by default
