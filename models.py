# models.py

from sqlalchemy import Column, String, Integer, DateTime, JSON
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.sql import func

Base = declarative_base()


class ProcessingRequest(Base):
    __tablename__ = "processing_requests"

    id = Column(Integer, primary_key=True, index=True)
    request_id = Column(String, unique=True, index=True, nullable=False)
    status = Column(
        String, default="Pending"
    )  
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())


class ProductImage(Base):
    __tablename__ = "product_images"

    id = Column(Integer, primary_key=True, index=True)
    request_id = Column(String, index=True, nullable=False)
    serial_number = Column(Integer, nullable=False)
    product_name = Column(String, nullable=False)
    input_image_urls = Column(JSON, nullable=False)
    output_image_urls = Column(JSON, nullable=True)
