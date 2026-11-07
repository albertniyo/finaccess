"""District boundaries for the choropleth map."""

from fastapi import APIRouter, Response

from compass import data

router = APIRouter()


@router.get("/districts")
def get_districts(response: Response) -> dict:
    """geoBoundaries ADM2 (simplified) with district and province names."""
    response.headers["Cache-Control"] = "public, max-age=86400"
    return data.load_geojson()
