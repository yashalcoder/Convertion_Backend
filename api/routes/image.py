from fastapi import APIRouter, UploadFile, File, HTTPException
from fastapi.responses import Response
from api.services.image_utils import convert_to_png,compress_image,convert_png_to_jpg,remove_background,resize_image,crop_image
import json
import traceback
from fastapi import APIRouter, UploadFile, File, HTTPException, Form

router = APIRouter()

@router.post("/convert")
async def convert_image(file: UploadFile = File(...)):
    try:
        content = await file.read()
        png_image = convert_to_png(content)

        return Response(
            content=png_image.getvalue(),
            media_type="image/png",
            headers={"Content-Disposition": "attachment; filename=converted.png"}
        )
    except Exception as e:
        print("❌ Exception in /convert:")
        traceback.print_exc()
        raise HTTPException(status_code=500, detail="Image conversion failed")
@router.post("/png-to-jpg")
async def png_to_jpg_route(
    file: UploadFile = File(...),
    quality: int = Form(90)
):
    try:
        content = await file.read()
        jpg_image = convert_png_to_jpg(content, quality=quality)

        return Response(
            content=jpg_image.getvalue(),
            media_type="image/jpeg",
            headers={"Content-Disposition": "attachment; filename=converted.jpg"}
        )

    except Exception as e:
        traceback.print_exc()
        raise HTTPException(status_code=500, detail="PNG to JPG conversion failed")

@router.post("/compress")
async def compress_image_route(
    file: UploadFile = File(...),
    compression_type: str = Form(...),
    quality: int = Form(80),
    target_size: int = Form(500),
    target_unit: str = Form("KB")
):
    try:
        content = await file.read()
        output = compress_image(content, compression_type, quality, target_size, target_unit)

        # Use Response instead of StreamingResponse
        return Response(
            content=output.getvalue(),
            media_type="image/jpeg",
            headers={"Content-Disposition": "attachment; filename=compressed.jpg"}
        )

    except Exception as e:
        traceback.print_exc()
        raise HTTPException(status_code=500, detail="Image compression failed")
@router.post("/remove-background")
async def remove_background_route(
    file: UploadFile = File(...),
    removal_mode: str = Form("auto"),
    background_type: str = Form("transparent"),
    background_color: str = Form("#ffffff")
):
    try:
        print("📥 API HIT: /remove-background")
        content = await file.read()
        print(f"📁 File received: {file.filename}, size: {len(content)} bytes")
        print("🔧 Parameters:", removal_mode, background_type, background_color)

        output = remove_background(
            image_bytes=content,
            background_type=background_type,
            background_color=background_color,
            removal_mode=removal_mode
        )

        print("✅ Background removed. Sending response...")
        return Response(
            content=output.getvalue(),
            media_type="image/png",
            headers={"Content-Disposition": "attachment; filename=bg_removed.png"}
        )

    except Exception as e:
        print("❌ Exception occurred:", e)
        traceback.print_exc()
        raise HTTPException(status_code=500, detail="Background removal failed")
@router.post("/resize-image")
async def resize_image_route(
    file: UploadFile = File(...),
    width: int = Form(...),
    height: int = Form(...),
    maintain_aspect: bool = Form(False)
):
    try:
        image_bytes = await file.read()
        output = resize_image(image_bytes, width, height, maintain_aspect)

        return Response(
            content=output.getvalue(),
            media_type="image/png",
            headers={"Content-Disposition": "attachment; filename=resized.png"}
        )

    except Exception as e:
        print("❌ Exception occurred:", e)
        raise HTTPException(status_code=500, detail="Image resize failed")
@router.post("/crop-image")
async def crop_image_route(
    file: UploadFile = File(...),
    crop_data: str = Form(...)
):
    try:
        crop_box = json.loads(crop_data)
        file_content = await file.read()
        cropped_io = crop_image(file_content, crop_box)

        return Response(
            content=cropped_io.read(),
            media_type="image/png",
            headers={"Content-Disposition": "attachment; filename=cropped.png"}
        )

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
