import datetime
import os
from selenium import webdriver
from selenium.webdriver.common.by import By

months = {
    1: "jan",
    2: "feb",
    3: "mar",
    4: "apr",
    5: "may",
    6: "june",
    7: "july",
    8: "aug",
    9: "sep",
    10: "oct",
    11: "nov",
    12: "dec"
}


def get_painting_url(year: int, month: int, day: int) -> str:
    url = f'https://www.hiroshimatsumoto.com/{year}paintings/works/' \
          f'{months[month]}{day if day > 9 else "0" + str(day)}{year}.jpg'
    print(url)
    return url


def download_image(image_url, save_path) -> None:
    op = webdriver.ChromeOptions()
    op.add_argument('headless')
    driver = webdriver.Chrome(options=op)
    driver.get(image_url)

    if not '404' in driver.title:
        with open(save_path, 'wb') as f:
            f.write(driver.find_element(By.XPATH, '/html/body/img').screenshot_as_png)
            print('downloaded')


def get_image(year: int, month: int, day: int) -> None:
    url = get_painting_url(year, month, day)

    if not os.path.exists(os.path.dirname(os.path.realpath(__file__)) + '/photos'):
        os.mkdir(os.path.dirname(os.path.realpath(__file__)) + '/photos')
        print('created /photos')

    if not os.path.exists(os.path.dirname(os.path.realpath(__file__)) + f'/photos/{year}'):
        os.mkdir(os.path.dirname(os.path.realpath(__file__)) + f'/photos/{year}')
        print(f'created /photos/{year}')

    if not os.path.exists(os.path.dirname(os.path.realpath(__file__)) + f'/photos/{year}/{month}'):
        os.mkdir(os.path.dirname(os.path.realpath(__file__)) + f'/photos/{year}/{month}')
        print(f'created /photos/{year}/{month}')

    if not os.path.exists(os.path.dirname(os.path.realpath(__file__)) + f'/photos/{year}/{month}/{day if day > 9 else "0" + str(day)}'):
        os.mkdir(os.path.dirname(os.path.realpath(__file__)) + f'/photos/{year}/{month}/{day if day > 9 else "0" + str(day)}')
        print(f'created /photos/{year}/{month}/{day}')

    download_image(url, os.path.dirname(os.path.realpath(__file__)) + f"/photos/{year}/{month}/{day if day > 9 else '0' + str(day)}/image.png")


def main() -> None:
    start_date = datetime.date(2006, 3, 1)
    end_date = datetime.date.today()

    while start_date < end_date:
        get_image(start_date.year, start_date.month, start_date.day)
        start_date += datetime.timedelta(days=1)


if __name__ == "__main__":
    main()
