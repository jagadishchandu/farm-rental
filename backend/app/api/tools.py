
from datetime import datetime
from fastapi import APIRouter, Depends, Query
from sqlalchemy import func
from sqlalchemy.orm import Session

from app.api.deps import get_db
from app.db.models import Tool, ToolInventory, RentalLine, RentalOrder

router = APIRouter(prefix="/tools", tags=["tools"])


def parse_dt(s: str) -> datetime:
    # Expect ISO-8601; e.g. "2026-03-16T10:00:00Z" or with offset
    return datetime.fromisoformat(s.replace("Z", "+00:00"))


@router.get("")
def list_tools(
    start: str | None = Query(default=None),
    end: str | None = Query(default=None),
    db: Session = Depends(get_db),
):
    start_dt = parse_dt(start) if start else None
    end_dt = parse_dt(end) if end else None

    tools = (
        db.query(Tool, ToolInventory.total_qty)
        .join(ToolInventory, ToolInventory.tool_id == Tool.id)
        .filter(Tool.active.is_(True))
        .all()
    )

    results = []
    for t, total_qty in tools:
        available = total_qty
        if start_dt and end_dt:
            booked = (
                db.query(func.coalesce(func.sum(RentalLine.qty), 0))
                .join(RentalOrder, RentalOrder.id == RentalLine.order_id)
                .filter(RentalLine.tool_id == t.id)
                .filter(RentalOrder.status == "confirmed")
                .filter(start_dt < RentalLine.end_ts)
                .filter(end_dt > RentalLine.start_ts)
                .scalar()
            )
            available = int(total_qty - booked)

        results.append(
            {
                "id": t.id,
                "name": t.name,
                "category": t.category,
                "description": t.description,
                "hourly_rate": float(t.hourly_rate),
                "image_url": t.image_url,
                "total_qty": int(total_qty),
                "available_qty": int(available),
            }
        )
    return results
