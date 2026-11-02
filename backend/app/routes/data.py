"""
Dataset exploration routes for GradeSense API.
"""

from typing import Optional
from fastapi import APIRouter, HTTPException, Query
from fastapi.responses import PlainTextResponse

from app.schemas import DatasetSummary, PaginatedRecords
from app.services.data_service import (
    load_dataset,
    get_dataset_summary,
    get_sample_records,
    is_dataset_available,
)

router = APIRouter(prefix="/dataset", tags=["Dataset"])


@router.get("/summary", response_model=DatasetSummary)
def get_summary() -> DatasetSummary:
    """Return schema, dimensions, missing value counts, and summary statistics."""
    if not is_dataset_available():
        raise HTTPException(
            status_code=404,
            detail="Dataset file not found. Please ensure student-mat.csv is in data/raw/.",
        )
    try:
        return get_dataset_summary()
    except Exception as exc:
        raise HTTPException(status_code=500, detail=f"Error inspecting dataset: {exc}")


@router.get("/records", response_model=PaginatedRecords)
def get_records(
    page: int = Query(1, ge=1, description="Page number"),
    page_size: int = Query(20, ge=1, le=100, description="Items per page"),
    search: Optional[str] = Query(None, description="Search term across all attributes"),
    school: Optional[str] = Query(None, description="Filter by school (GP or MS)"),
    sex: Optional[str] = Query(None, description="Filter by sex (F or M)"),
) -> PaginatedRecords:
    """Return paginated, searchable, and filtered dataset records."""
    if not is_dataset_available():
        raise HTTPException(status_code=404, detail="Dataset not found.")

    filters = {}
    if school:
        filters["school"] = school
    if sex:
        filters["sex"] = sex

    return get_sample_records(
        page=page,
        page_size=page_size,
        search=search,
        filters=filters if filters else None,
    )


@router.get("/export/csv")
def export_csv():
    """Export the raw dataset as a CSV text download."""
    if not is_dataset_available():
        raise HTTPException(status_code=404, detail="Dataset not found.")
    df = load_dataset()
    csv_str = df.to_csv(index=False)
    return PlainTextResponse(
        content=csv_str,
        media_type="text/csv",
        headers={"Content-Disposition": 'attachment; filename="student-mat-export.csv"'},
    )
