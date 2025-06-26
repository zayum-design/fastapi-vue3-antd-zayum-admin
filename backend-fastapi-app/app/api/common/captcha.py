from fastapi import APIRouter
from fastapi.responses import StreamingResponse
from app.core.captcha import generate_captcha

router = APIRouter(prefix="/captcha", tags=["captcha"])

@router.get("", response_class=StreamingResponse)
async def get_captcha():
    captcha_id, image_bytes = await generate_captcha()
    headers = {"X-Captcha-Id": captcha_id}
    # StreamingResponse instead of Response
    return StreamingResponse(iter([image_bytes]), media_type="image/png", headers=headers)
