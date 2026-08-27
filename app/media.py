"""Safe handling for the single optional image attached to a post."""

from __future__ import annotations

import secrets
from pathlib import Path

from PIL import Image, UnidentifiedImageError


IMAGE_EXTENSIONS = {"JPEG": "jpg", "PNG": "png", "WEBP": "webp"}


class InvalidImageError(ValueError):
    """Raised when an uploaded file is not an allowed image."""


def save_post_image(file_storage, media_root) -> str:
    """Verify and persist an uploaded image under a generated filename."""

    try:
        image = Image.open(file_storage.stream)
        image.verify()
        image_format = image.format
    except (Image.DecompressionBombError, OSError, SyntaxError, UnidentifiedImageError) as exc:
        raise InvalidImageError("Datoteka ni veljavna slika.") from exc
    finally:
        file_storage.stream.seek(0)

    extension = IMAGE_EXTENSIONS.get(image_format)
    if extension is None:
        raise InvalidImageError("Dovoljene so le slike JPEG, PNG in WebP.")

    target_directory = Path(media_root) / "posts"
    target_directory.mkdir(parents=True, exist_ok=True)
    filename = f"{secrets.token_hex(16)}.{extension}"
    file_storage.save(target_directory / filename)
    return filename


def delete_post_image(filename: str | None, media_root) -> None:
    """Remove a generated image filename without accepting a path traversal target."""

    if not filename or Path(filename).name != filename:
        return
    path = Path(media_root) / "posts" / filename
    path.unlink(missing_ok=True)
