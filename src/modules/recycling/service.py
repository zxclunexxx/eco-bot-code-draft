from sqlalchemy import select
from sqlalchemy.orm import Session

from src.core.models import Material, PointMaterial, RecyclingPoint
from src.integrations.maps import google_maps_route_url
from src.modules.recycling.geo import distance_meters


class RecyclingPointService:
    def list_materials(self, db: Session) -> list[str]:
        materials = db.scalars(select(Material).order_by(Material.name)).all()
        return [material.name for material in materials]

    def find_by_material(
        self,
        db: Session,
        material_name: str,
        user_lat: float | None = None,
        user_lon: float | None = None,
    ) -> list[dict]:
        material = db.scalar(select(Material).where(Material.name == material_name))
        if not material:
            return []

        rows = db.execute(
            select(RecyclingPoint)
            .join(PointMaterial, PointMaterial.point_id == RecyclingPoint.id)
            .where(
                PointMaterial.material_id == material.id,
                RecyclingPoint.is_active.is_(True),
            )
        ).scalars().all()

        result = []
        for point in rows:
            distance = None
            if user_lat is not None and user_lon is not None:
                distance = distance_meters(user_lat, user_lon, point.latitude, point.longitude)
            result.append({
                "id": point.id,
                "name": point.name,
                "address": point.address,
                "working_hours": point.working_hours,
                "conditions": point.conditions,
                "latitude": point.latitude,
                "longitude": point.longitude,
                "distance_m": distance,
            })

        if user_lat is not None and user_lon is not None:
            return sorted(result, key=lambda item: item["distance_m"] or 10**12)
        return sorted(result, key=lambda item: item["name"])

    def get_point_details(
        self,
        db: Session,
        point_id: int,
        user_lat: float | None = None,
        user_lon: float | None = None,
    ) -> dict | None:
        point = db.get(RecyclingPoint, point_id)
        if not point:
            return None

        route_url = google_maps_route_url(point.latitude, point.longitude, user_lat, user_lon)
        return {
            "id": point.id,
            "name": point.name,
            "address": point.address,
            "working_hours": point.working_hours,
            "conditions": point.conditions,
            "route_url": route_url,
        }
