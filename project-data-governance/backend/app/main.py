from fastapi import FastAPI, HTTPException
from sqlalchemy.orm import Session
from app.db import engine, SessionLocal, Base
from app.models.user import User
from app.core.security import hash_password, verify_password, create_access_token
from app.schemas.user import UserCreate
from app.dependencies.auth import get_current_user
from fastapi import Depends
from app.dependencies.auth import require_role
from app.models.audit_log import AuditLog
from app.services.audit import log_action
from fastapi import Request
from app.middleware.audit import AuditMiddleware
from app.models.dataset import Dataset
from app.schemas.dataset import DatasetCreate, DatasetResponse



app = FastAPI()
app.add_middleware(AuditMiddleware)

Base.metadata.create_all(bind=engine)

# Dependency DB
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


# REGISTER
@app.post("/register")
def register(user: UserCreate):
    db = SessionLocal()

    print("PASSWORD:", user.password)
    print("TYPE:", type(user.password))
    print("LENGTH:", len(user.password))

    existing = db.query(User).filter(User.email == user.email).first()
    if existing:
        raise HTTPException(status_code=400, detail="Email already registered")

    new_user = User(
        email=user.email,
        password=hash_password(user.password)
    )

    db.add(new_user)
    db.commit()
    db.close()

    return {"message": "User created"}


# LOGIN
@app.post("/login")
def login(user: UserCreate):
    db = SessionLocal()

    db_user = db.query(User).filter(User.email == user.email).first()

    if not db_user or not verify_password(user.password, db_user.password):
        raise HTTPException(status_code=401, detail="Invalid credentials")

    token = create_access_token({"sub": db_user.email})

    return {
        "access_token": token,
        "token_type": "bearer"
    }

#PROTECTED ADMIN ACCOUNT
@app.get("/protected")
def protected(request: Request, user=Depends(get_current_user)):
    db = SessionLocal()

    log_action(
        db=db,
        user_email=user.email,
        action="ACCESS_PROTECTED",
        endpoint=str(request.url.path),
        method=request.method
    )

    db.close()

    return {
        "message": "You are authorized",
        "user": user.email
    }

# CEK ADMIN ONLY
@app.get("/admin-only") 
def admin_only(user=Depends(require_role("admin"))):
    return {
        "message": "Welcome Admin",
        "email": user.email,
        "role": user.role
    }


#ENDPOINT DATASETS
@app.post("/datasets", response_model=DatasetResponse)
def create_dataset(data: DatasetCreate, user=Depends(get_current_user)):
    db = SessionLocal()

    dataset = Dataset(
        name=data.name,
        description=data.description,
        owner_email=user.email
    )

    db.add(dataset)
    db.commit()
    db.refresh(dataset)
    db.close()

    return dataset

#CHECK LIST DATASETS
@app.get("/datasets", response_model=list[DatasetResponse])
def get_datasets(user=Depends(get_current_user)):
    db = SessionLocal()

    datasets = db.query(Dataset).all()

    db.close()
    return datasets


#DATASET
@app.get("/datasets/{dataset_id}", response_model=DatasetResponse)
def get_dataset(dataset_id: int, user=Depends(get_current_user)):
    db = SessionLocal()

    dataset = db.query(Dataset).filter(Dataset.id == dataset_id).first()

    if not dataset:
        db.close()
        raise HTTPException(status_code=404, detail="Dataset not found")

    db.close()
    return dataset



@app.put("/datasets/{dataset_id}", response_model=DatasetResponse)
def update_dataset(dataset_id: int, data: DatasetCreate, user=Depends(get_current_user)):
    db = SessionLocal()

    dataset = db.query(Dataset).filter(Dataset.id == dataset_id).first()

    if not dataset:
        db.close()
        raise HTTPException(status_code=404, detail="Dataset not found")

    # CEK PEMILIK DATASETS
    if dataset.owner_email != user.email:
        db.close()
        raise HTTPException(status_code=403, detail="Forbidden")

    dataset.name = data.name
    dataset.description = data.description

    db.commit()
    db.refresh(dataset)
    db.close()

    return dataset


#HAPUS DATASET
@app.delete("/datasets/{dataset_id}")
def delete_dataset(dataset_id: int, user=Depends(get_current_user)):
    db = SessionLocal()

    dataset = db.query(Dataset).filter(Dataset.id == dataset_id).first()

    if not dataset:
        db.close()
        raise HTTPException(status_code=404, detail="Dataset not found")

    # CHECK DATASET PEMILIK
    if dataset.owner_email != user.email:
        db.close()
        raise HTTPException(status_code=403, detail="Forbidden")

    db.delete(dataset)
    db.commit()
    db.close()

    return {"message": "Dataset deleted"}