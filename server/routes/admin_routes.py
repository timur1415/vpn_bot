from datetime import datetime
from pathlib import Path

from fastapi import APIRouter, HTTPException, Request
from fastapi.responses import FileResponse

from config.config import ADMIN_ID
from db.db import (
    delete_all_expired_paid_users,
    delete_paid_user_if_expired,
    delete_user_data_by_telegram_id,
    get_bot_visitors_count,
    list_paid_users,
)

router = APIRouter()
ADMIN_TEMPLATE = Path(__file__).resolve().parents[2] / "templates" / "admin.html"


def _check_admin(request: Request) -> None:
    tg_id = request.query_params.get("tg_id")
    if not tg_id or tg_id != str(ADMIN_ID):
        raise HTTPException(status_code=403, detail="Forbidden")


def _days_left(expires_at):
    if not expires_at:
        return None
    return (expires_at.date() - datetime.utcnow().date()).days


@router.get("/admin")
async def admin_page(request: Request):
    _check_admin(request)
    return FileResponse(ADMIN_TEMPLATE)


@router.get("/admin/api/users")
async def admin_users(request: Request):
    _check_admin(request)
    users = await list_paid_users()
    visitors_count = await get_bot_visitors_count()

    payload = []
    for user in users:
        days_left = _days_left(user.expires_at)
        payload.append(
            {
                "id": user.id,
                "telegram_id": user.telegram_id,
                "username": user.username,
                "tariff": user.tariff,
                "status": user.status,
                "started_at": user.started_at.isoformat(sep=" ") if user.started_at else None,
                "expires_at": user.expires_at.isoformat(sep=" ") if user.expires_at else None,
                "days_left": days_left,
                "created_at": user.created_at.isoformat(sep=" ") if user.created_at else None,
            }
        )

    return {"users": payload, "visitors_count": visitors_count}


@router.delete("/admin/api/users/delete-expired")
async def admin_delete_all_expired_users(request: Request):
    _check_admin(request)

    deleted_count = await delete_all_expired_paid_users()
    return {"ok": True, "deleted_count": deleted_count}


@router.delete("/admin/api/users/{telegram_id}")
async def admin_delete_expired_user(telegram_id: int, request: Request, force: bool = False):
    _check_admin(request)

    if force:
        deleted = await delete_user_data_by_telegram_id(telegram_id)
        if sum(deleted.values()) == 0:
            raise HTTPException(status_code=404, detail="Пользователь не найден")
        return {"ok": True, "force": True, "deleted": deleted}

    deleted = await delete_paid_user_if_expired(telegram_id)
    if not deleted:
        raise HTTPException(
            status_code=400,
            detail="Можно удалить только пользователя с истекшей подпиской",
        )

    return {"ok": True}