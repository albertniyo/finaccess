"""Source citations and metadata."""

from fastapi import APIRouter

from compass import sources

router = APIRouter()


@router.get("/sources")
def get_sources() -> dict:
    """Citations, years, and geographic levels for displayed statistics."""
    return sources.list_sources()