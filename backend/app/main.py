
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.core.config import settings
from app.api.auth import router as auth_router
from app.api.tools import router as tools_router
from app.api.orders import router as orders_router
from app.api.admin import router as admin_router

app = FastAPI(title="Farm Rental API")

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins_list,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(auth_router)
app.include_router(tools_router)
app.include_router(orders_router)
app.include_router(admin_router)


@app.get("/health")
def health():
    return {"ok": True}
