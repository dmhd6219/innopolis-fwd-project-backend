import datetime
import io

import PIL.Image as Image


def save_photo(image: bytes, date: datetime.date):
    path = f'/{date.year}/{date.month}/{date.day}/image.png'

    io_bytes = io.BytesIO(image)
    img = Image.open(io_bytes)
    img.save(path)
