
from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel, Field
from sqlalchemy.orm import Session

from app.api.deps import get_db, require_admin
from app.db.models import Tool, ToolInventory, RentalOrder



router = APIRouter(prefix="/admin", tags=["admin"])


class ToolIn(BaseModel):
    name: str
    category: str = "general"
    description: str = ""
    hourly_rate: float = 0
    image_url: str = ""
    active: bool = True
    total_qty: int = Field(ge=0)



@router.get("/tools")
def list_tools_admin(db: Session = Depends(get_db), _admin=Depends(require_admin)):
    rows = (
        db.query(Tool, ToolInventory.total_qty)
        .join(ToolInventory, ToolInventory.tool_id == Tool.id)
        .order_by(Tool.id.desc())
        .all()
    )
    return [
        {
            "id": t.id,
            "name": t.name,
            "category": t.category,
            "description": t.description,
            "hourly_rate": float(t.hourly_rate),
            "image_url": t.image_url,
            "active": bool(t.active),
            "total_qty": int(total_qty),
        }
        for (t, total_qty) in rows
    ]



@router.get("/tools/{tool_id}")
def get_tool_admin(tool_id: int, db: Session = Depends(get_db), _admin=Depends(require_admin)):
    row = (
        db.query(Tool, ToolInventory.total_qty)
        .join(ToolInventory, ToolInventory.tool_id == Tool.id)
        .filter(Tool.id == tool_id)
        .first()
    )
    if not row:
        raise HTTPException(status_code=404, detail="Tool not found")
    t, total_qty = row
    return {
        "id": t.id,
        "name": t.name,
        "category": t.category,
        "description": t.description,
        "hourly_rate": float(t.hourly_rate),
        "image_url": t.image_url,
        "active": bool(t.active),
        "total_qty": int(total_qty),
    }



class SetInventoryIn(BaseModel):
    total_qty: int = Field(ge=0)


@router.put("/tools/{tool_id}/inventory")
def set_inventory(tool_id: int, payload: SetInventoryIn, db: Session = Depends(get_db), _admin=Depends(require_admin)):
    inv = db.query(ToolInventory).filter(ToolInventory.tool_id == tool_id).first()
    if not inv:
        inv = ToolInventory(tool_id=tool_id, total_qty=payload.total_qty)
        db.add(inv)
    else:
        inv.total_qty = payload.total_qty
    db.commit()
    return {"message": "inventory set"}


@router.delete("/tools/{tool_id}")
def delete_tool(tool_id: int, db: Session = Depends(get_db), _admin=Depends(require_admin)):
    tool = db.query(Tool).filter(Tool.id == tool_id).first()
    if not tool:
        raise HTTPException(status_code=404, detail="Tool not found")
    db.delete(tool)
    db.commit()
    return {"message": "deleted"}


@router.get("/orders")
def list_orders(db: Session = Depends(get_db), _admin=Depends(require_admin)):
    orders = db.query(RentalOrder).order_by(RentalOrder.id.desc()).limit(100).all()
    return [
        {
            "id": o.id,
            "user_id": o.user_id,
            "status": o.status,
            "created_at": o.created_at.isoformat(),
            "lines": [
                {
                    "tool_id": l.tool_id,
                    "qty": l.qty,
                    "start_ts": l.start_ts.isoformat(),
                    "end_ts": l.end_ts.isoformat(),
                }
                for l in o.lines
            ],
        }
        for o in orders
    ]
