from fastapi import APIRouter, HTTPException, Response
from pydantic import BaseModel
from typing import Any, Dict
from app.services.export_service import ExportService
import asyncio

router = APIRouter()

class ExportRequest(BaseModel):
    data: Dict[str, Any]
    type: str  # 'forecast' or 'backtest'

@router.post("/pdf")
async def export_to_pdf(request: ExportRequest):
    """Export data to PDF format"""
    try:
        export_service = ExportService()
        pdf_content = await export_service.export_to_pdf(
            data=request.data,
            export_type=request.type
        )
        
        return Response(
            content=pdf_content,
            media_type="application/pdf",
            headers={"Content-Disposition": f"attachment; filename={request.type}_report.pdf"}
        )
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"PDF export failed: {str(e)}")

@router.post("/csv")
async def export_to_csv(request: ExportRequest):
    """Export data to CSV format"""
    try:
        export_service = ExportService()
        csv_content = await export_service.export_to_csv(
            data=request.data,
            export_type=request.type
        )
        
        return Response(
            content=csv_content,
            media_type="text/csv",
            headers={"Content-Disposition": f"attachment; filename={request.type}_data.csv"}
        )
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"CSV export failed: {str(e)}")

@router.post("/summary")
async def generate_summary(request: ExportRequest):
    """Generate a shareable text summary"""
    try:
        export_service = ExportService()
        summary = await export_service.generate_summary(
            data=request.data,
            export_type=request.type
        )
        
        return {"summary": summary}
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Summary generation failed: {str(e)}")
