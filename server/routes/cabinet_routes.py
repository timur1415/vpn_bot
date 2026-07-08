from datetime import datetime
from pathlib import Path

from fastapi import APIRouter, HTTPException, Request
from fastapi.responses import FileResponse

from db.db import get_paid_user, get_user_payments

router = APIRouter()
CABINET_TEMPLATE = Path(__file__).resolve().parents[2] / "templates" / "index.html"


def _days_left(expires_at):
    if not expires_at:
        return None
    return (expires_at.date() - datetime.utcnow().date()).days


def _require_tg_id(request: Request) -> int:
    tg_id = request.query_params.get("tg_id")
    if not tg_id or not tg_id.isdigit():
        raise HTTPException(status_code=403, detail="Forbidden")
    return int(tg_id)


@router.get("/cabinet")
async def cabinet_page(request: Request):
    _require_tg_id(request)
    return FileResponse(CABINET_TEMPLATE)


@router.get("/cabinet/api/profile")
async def cabinet_profile(request: Request):
    tg_id = _require_tg_id(request)

    paid_user = await get_paid_user(tg_id)
    payments = await get_user_payments(tg_id, limit=10)

    if not paid_user:
        return {
            "user": None,
            "payments": [],
        }

    return {
        "user": {
            "id": paid_user.id,
            "telegram_id": paid_user.telegram_id,
            "username": paid_user.username,
            "tariff": paid_user.tariff,
            "status": paid_user.status,
            "started_at": paid_user.started_at.isoformat(sep=" ") if paid_user.started_at else None,
            "expires_at": paid_user.expires_at.isoformat(sep=" ") if paid_user.expires_at else None,
            "days_left": _days_left(paid_user.expires_at),
            "warned_3_at": paid_user.warned_3_at.isoformat(sep=" ") if paid_user.warned_3_at else None,
            "warned_2_at": paid_user.warned_2_at.isoformat(sep=" ") if paid_user.warned_2_at else None,
            "warned_1_at": paid_user.warned_1_at.isoformat(sep=" ") if paid_user.warned_1_at else None,
            "created_at": paid_user.created_at.isoformat(sep=" ") if paid_user.created_at else None,
        },
        "payments": [
            {
                "id": payment.id,
                "transaction_id": payment.transaction_id,
                "tariff": payment.tariff,
                "amount": payment.amount,
                "status": payment.status,
                "created_at": payment.created_at.isoformat(sep=" ") if payment.created_at else None,
                "paid_at": payment.paid_at.isoformat(sep=" ") if payment.paid_at else None,
                "renew_at": payment.renew_at.isoformat(sep=" ") if payment.renew_at else None,
            }
            for payment in payments
        ],
    }