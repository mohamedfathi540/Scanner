from sqlalchemy import Column, Integer, String, DateTime, ForeignKey
from sqlalchemy.sql import func
from .minirag_base import SQLAlchemyBase

class Project(SQLAlchemyBase):
    """
    Repurposed to log the processing of manufacturing production reports.
    Kept the class name 'Project' to minimize import errors across the app.
    """
    __tablename__ = 'production_report_logs'

    id = Column(Integer, primary_key=True, index=True)
    filename = Column(String, index=True, nullable=False)
    
    # Removed user_id as login is no longer needed
    
    # Tracks how many rows of data (e.g., Oval seats, pillows) were extracted
    rows_extracted = Column(Integer, default=0)
    
    # Logs if the OCR to Excel conversion was successful
    status = Column(String, default='SUCCESS')
    
    # Automatically timestamps when the Excel file was generated
    processed_at = Column(DateTime(timezone=True), server_default=func.now())