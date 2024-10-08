
from fastapi import FastAPI, File, UploadFile, HTTPException, Depends
from fastapi.responses import JSONResponse
from fastapi.staticfiles import StaticFiles
from sqlalchemy.orm import Session
from models import Base, ProcessingRequest, ProductImage
import uuid
import csv
import io
import os

app = FastAPI()

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

DATABASE_URL = "postgresql://postgres:postgres@localhost/spyne-local"

engine = create_engine(DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


Base.metadata.create_all(bind=engine)

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

app.mount(
    "/images",
    StaticFiles(directory=os.path.join(os.path.dirname(__file__), "processed_images")),
    name="images",
)


@app.post("/upload")
async def upload_csv(file: UploadFile = File(...), db: Session = Depends(get_db)):
    if not file.filename.endswith(".csv"):
        raise HTTPException(
            status_code=400, detail="Invalid file format. Only CSV files are accepted."
        )
    content = await file.read()
    try:
        
        decoded = content.decode("utf-8").strip()

        
        lines = decoded.split("\r\n")
        cleaned_content = "\n".join(line.strip('"') for line in lines if line.strip())

        
        reader = csv.reader(io.StringIO(cleaned_content))

        
        headers = next(reader)
        required_fields = ["Serial Number", "Product Name"]
        if headers[:2] != required_fields:
            raise ValueError(f"Missing or incorrect required fields: {headers[:2]}")


        request_id = str(uuid.uuid4())


        for row in reader:
            if len(row) < 3:
                raise ValueError(
                    "Each row must contain at least Serial Number, Product Name, and one image URL"
                )

            serial_number = int(row[0]) 
            product_name = row[1].strip()  
            input_image_urls = row[2:]  

            
            if not input_image_urls:
                raise ValueError("Input Image Urls must contain at least one URL")

            
            product_image = ProductImage(
                request_id=request_id,
                serial_number=serial_number,
                product_name=product_name,
                input_image_urls=input_image_urls,  
            )
            db.add(product_image)

        
        processing_request = ProcessingRequest(request_id=request_id, status="Pending")
        db.add(processing_request)
        db.commit()
        print("After Commit")

        return JSONResponse(content={"request_id": request_id})

    except ValueError as ve:
        raise HTTPException(status_code=400, detail=str(ve))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"An error occurred: {str(e)}")