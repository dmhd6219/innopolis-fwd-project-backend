import datetime
import io
import os

import PIL.Image as Image


def save_photo(image: bytes, date: datetime.date):
    real_path = '\\'.join(os.path.dirname(os.path.realpath(__file__)).split('\\')[:-1:])
    if not os.path.exists(real_path + '/photos'):
        os.mkdir(real_path + '/photos')
        print('created /photos')

    if not os.path.exists(real_path + f'/photos/{date.year}'):
        os.mkdir(real_path + f'/photos/{date.year}')
        print(f'created /photos/{date.year}')

    if not os.path.exists(real_path + f'/photos/{date.year}/{date.month}'):
        os.mkdir(real_path + f'/photos/{date.year}/{date.month}')
        print(f'created /photos/{date.year}/{date.month}')

    if not os.path.exists(
            real_path + f'/photos/{date.year}/{date.month}/{date.day if date.day > 9 else "0" + str(date.day)}'):
        os.mkdir(real_path + f'/photos/{date.year}/{date.month}/{date.day if date.day > 9 else "0" + str(date.day)}')
        print(f'created /photos/{date.year}/{date.month}/{date.day}')

    path = real_path + f'\\photos\\{date.year if date.year > 9 else "0" + str(date.year)}\\' \
                       f'{date.month}\\{date.day if date.day > 9 else "0" + str(date.day)}\\image.png'

    print(path)

    io_bytes = io.BytesIO(image)
    img = Image.open(io_bytes)

    # img = Image.open(image)

    img.save(path)
