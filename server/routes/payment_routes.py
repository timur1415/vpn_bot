from fastapi import APIRouter, Request

router = APIRouter()

@router.post("/payment/callback")
async def payment_callback(request: Request):
    data = await request.json()

    print(data)

    return {'status': 'ok'}