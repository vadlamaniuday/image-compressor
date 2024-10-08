from celery_app import celery
from sqlalchemy.orm import sessionmaker
from sqlalchemy import create_engine
from models import ProcessingRequest, ProductImage
import requests
from PIL import Image
import io
import uuid
import os

DATABASE_URL = "postgresql://postgres:postgres@localhost/spyne-local"
engine = create_engine(DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


PROCESSED_IMAGES_DIR = os.path.join(os.path.dirname(__file__), "processed_images")

os.makedirs(PROCESSED_IMAGES_DIR, exist_ok=True)

BASE_IMAGE_URL = "http://localhost:8000/images"


@celery.task
def process_images_task(request_id: str):
    db = SessionLocal()
    try:

        processing_request = (
            db.query(ProcessingRequest).filter_by(request_id=request_id).first()
        )
        if not processing_request:
            return
        processing_request.status = "In Progress"
        db.commit()


        product_images = db.query(ProductImage).filter_by(request_id=request_id).all()

        for product_image in product_images:
            output_urls = []
            for url in product_image.input_image_urls:
                try:
                    response = requests.get(url, timeout=10)
                    response.raise_for_status()
                    image = Image.open(io.BytesIO(response.content))

                    img_byte_arr = io.BytesIO()

                    image.save(img_byte_arr, format=image.format, quality=50)
                    img_byte_arr = img_byte_arr.getvalue()

                    filename = f"{uuid.uuid4()}.{image.format.lower()}"
                    file_path = os.path.join(PROCESSED_IMAGES_DIR, filename)

                    with open(file_path, "wb") as f:
                        f.write(img_byte_arr)

                    output_url = f"{BASE_IMAGE_URL}/{filename}"
                    output_urls.append(output_url)

                except Exception as e:

                    output_urls.append(None)  


            product_image.output_image_urls = output_urls
            db.commit()


        processing_request.status = "Completed"
        db.commit()

    except Exception as e:

        if processing_request:
            processing_request.status = "Failed"
            db.commit()

    finally:
        db.close()
