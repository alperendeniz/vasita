import sqlalchemy as sa
from flask import jsonify, request

from app import db
from app.api import api
from app.models import Vehicle, Complaint


@api.route("/vehicles", methods=["GET"])
def get_vehicles():
    """Tüm araçları sayfalama (pagination) ile döndürür."""
    page = request.args.get("page", 1, type=int)
    per_page = request.args.get("per_page", 10, type=int)

    # SQLAlchemy 2.x standardı ile araçları çek
    stmt = sa.select(Vehicle).order_by(Vehicle.id.desc())
    pagination = db.paginate(stmt, page=page, per_page=per_page, error_out=False)

    return jsonify({
        "data": [vehicle.to_dict() for vehicle in pagination.items],
        "meta": {
            "current_page": pagination.page,
            "total_pages": pagination.pages,
            "has_next": pagination.has_next,
            "total_items": pagination.total
        }
    })


@api.route("/vehicles/<int:id>", methods=["GET"])
def get_vehicle_detail(id: int):
    """Belirli bir aracı ve o araca ait ONAYLANMIŞ şikayetleri döndürür."""
    stmt = sa.select(Vehicle).where(Vehicle.id == id)
    vehicle = db.session.execute(stmt).scalar_one_or_none()

    if not vehicle:
        return jsonify({"error": "Vehicle not found"}), 404

    # Araca ait ONAYLANMIŞ şikayetleri çek
    complaint_stmt = sa.select(Complaint).where(
        Complaint.vehicle_id == vehicle.id,
        Complaint.is_verified == True
    ).order_by(Complaint.created_at.desc())
    
    verified_complaints = db.session.execute(complaint_stmt).scalars().all()

    # Aracı JSON'a çevirip içerisine şikayetleri göm
    vehicle_dict = vehicle.to_dict()
    vehicle_dict["complaints"] = [complaint.to_dict() for complaint in verified_complaints]

    return jsonify(vehicle_dict)
