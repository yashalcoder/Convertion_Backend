from PIL import Image
import io
import time
from rembg import remove, new_session
from io import BytesIO

def convert_to_png(image_bytes):
    

    start = time.time()

    try:
        image = Image.open(io.BytesIO(image_bytes))

        if image.mode in ("RGBA", "P"):
            image = image.convert("RGB")

        output = io.BytesIO()
        image.save(output, format="PNG")
        output.seek(0)

        print(f"✅ Converted in {round(time.time() - start, 2)}s")
        return output
    except Exception as e:
        print("❌ Conversion Error:", e)
        raise
def convert_png_to_jpg(image_bytes: bytes, quality: int = 90) -> io.BytesIO:
    try:
        image = Image.open(io.BytesIO(image_bytes))

        if image.mode in ("RGBA", "P"):
            image = image.convert("RGB")

        output = io.BytesIO()
        image.save(output, format="JPEG", quality=quality, optimize=True)
        output.seek(0)
        return output

    except Exception as e:
        print("❌ PNG to JPG conversion error:", e)
        raise
def compress_image(content: bytes, compression_type: str, quality: int, target_size: int, target_unit: str) -> io.BytesIO:
    img = Image.open(io.BytesIO(content))

    output_io = io.BytesIO()

    if compression_type == "quality":
        img = img.convert("RGB")
        img.save(output_io, format="JPEG", quality=quality, optimize=True)

    elif compression_type == "size":
        img = img.convert("RGB")
        quality_guess = 85
        img.save(output_io, format="JPEG", quality=quality_guess, optimize=True)

        # 🧠 Loop to shrink if not below target
        target_bytes = target_size * {
            "KB": 1024,
            "MB": 1024**2,
            "GB": 1024**3,
        }[target_unit.upper()]

        while output_io.tell() > target_bytes and quality_guess > 10:
            quality_guess -= 5
            output_io = io.BytesIO()
            img.save(output_io, format="JPEG", quality=quality_guess, optimize=True)

    else:
        raise ValueError("Invalid compression type")

    output_io.seek(0)
    return output_io


def remove_background(
    image_bytes: bytes,
    background_type: str = "transparent",
    background_color: str = "#ffffff",
    removal_mode: str = "u2netp",
) -> io.BytesIO:
    try:
        input_image = Image.open(io.BytesIO(image_bytes)).convert("RGBA")

        # Use a specific model (faster and avoids download issues)
        session = new_session("u2netp")  # ✅ explicitly load smaller model
        result = remove(input_image, session=session)

        result_image = remove(input_image, session=session).convert("RGBA")
        

        if background_type == "color":
            bg = Image.new("RGBA", result_image.size, background_color)
            result_image = Image.alpha_composite(bg, result_image)

        elif background_type == "white":
            bg = Image.new("RGBA", result_image.size, "#ffffff")
            result_image = Image.alpha_composite(bg, result_image)
        elif background_type == "black":
            bg = Image.new("RGBA", result_image.size, "#000000")
            result_image = Image.alpha_composite(bg, result_image)

        output = io.BytesIO()
        result_image.save(output, format="PNG")
        output.seek(0)
        return output

    except Exception as e:
        print("❌ Background removal error:", e)
        raise

def resize_image(image_bytes: bytes, width: int, height: int, maintain_aspect: bool = True) -> io.BytesIO:
    try:
        image = Image.open(io.BytesIO(image_bytes))

        # Handle Pillow version compatibility
        try:
            resample_filter = Image.Resampling.LANCZOS
        except AttributeError:
            resample_filter = Image.LANCZOS

        if maintain_aspect:
            image.thumbnail((width, height), resample=resample_filter)
            resized_image = image
        else:
            resized_image = image.resize((width, height), resample=resample_filter)

        output = io.BytesIO()
        resized_image.save(output, format="PNG")
        output.seek(0)
        return output

    except Exception as e:
        print("❌ Resize error:", e)
        raise
def crop_image(file: bytes, crop_box: dict):
    with Image.open(BytesIO(file)) as img:
        width, height = img.size

        # Convert crop percentages to actual pixel values
        left = int((crop_box["x"] / 100) * width)
        top = int((crop_box["y"] / 100) * height)
        right = left + int((crop_box["width"] / 100) * width)
        bottom = top + int((crop_box["height"] / 100) * height)

        cropped = img.crop((left, top, right, bottom))

        output = BytesIO()
        cropped.save(output, format="PNG")
        output.seek(0)
        return output
