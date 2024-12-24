import asyncio
import sys
from playwright.async_api import async_playwright
from fake_useragent import FakeUserAgent
import json
from pathlib import Path
import requests

API_TOKEN = '8005517380:AAGxa2KjbwDrM0ndrGYIDB0TTh6dLzFN-SY'

async def send_message(chat_id, text):
    """Функция для отправки сообщения пользователю в Telegram."""
    url = f"https://api.telegram.org/bot{API_TOKEN}/sendMessage"
    data = {"chat_id": chat_id, "text": text}
    requests.post(url, data=data)


async def main():
    min_price = sys.argv[1]
    max_price = sys.argv[2]
    chat_id = sys.argv[3]

    async with async_playwright() as p:

        #Run browser with chromium
        browser = await p.chromium.launch(
            headless=False, args=["--disable-blink-features=AutomationControlled"]
        )

        #Fake User Agent for run browser
        user_agent = FakeUserAgent().random
        await browser.new_context(user_agent=user_agent)

        #Cookie for run browser
        context = await browser.new_context()
        await context.add_cookies(json.loads(Path("cookies.json").read_text()))
        page = await context.new_page()

        #Work main page
        page_count = 1
        await page.goto(
            f"https://auto.drom.ru/all/page{page_count}/?minprice={min_price}&maxprice={max_price}",
            wait_until="domcontentloaded",
        )

        results = []

        while True:  #For main page
            while True:  #For car page
                car_page = page.locator(
                    "//html/body/div[2]/div[4]/div[1]/div[1]/div[5]/div/div[1]/div/div[2]/div[1]/a/h3"
                )
                car_count = await car_page.count()

                i = 0
                while i < car_count:
                    car = car_page.nth(i)
                    await car.click()
                    await page.wait_for_load_state("domcontentloaded")

                    #Name car in car_page
                    car_name_locator = page.locator(
                        "//html/body/div[2]/div[3]/div[2]/h1/span"
                    )
                    car_name = await car_name_locator.text_content()

                    #Price car in car_page
                    car_price_locator = page.locator(
                        "//html/body/div[2]/div[4]/div[1]/div[1]/div[2]/div[2]/div[1]/div/div[1]"
                    )
                    car_price = await car_price_locator.text_content()


                    #Attributes
                    elements_car_locator = page.locator(
                        "//html/body/div[2]/div[4]/div[1]/div[1]/div[2]/div[2]/div/table/tbody/tr/th"
                    )
                    elements = await elements_car_locator.all_text_contents()

                    #Descriptions
                    descriptions_car_locator = page.locator(
                        "//html/body/div[2]/div[4]/div[1]/div[1]/div[2]/div[2]/div[2]/table/tbody/tr/td"
                    )
                    descriptions = await descriptions_car_locator.all_text_contents()
                    descriptions.pop(2)

                    #Check photo car
                    try:
                        photo_car = page.locator(
                            "//html/body/div[2]/div[4]/div[1]/div[1]/div[2]/div[1]/div[1]/div/div/div[1]/a/div/div/div/div/img"
                        )
                        if await photo_car.count() > 0:
                            src = await photo_car.get_attribute("src")
                            print(src)
                        else:
                            src = "https://xn--90aha1bhcc.xn--p1ai/img/placeholder.png"
                    except Exception as e:
                        print(f"Ошибка при получении фото: {e}")

                    # #Output info about car
                    # print(f"Название: {car_name[7:]}")
                    # print(f"Цена: {car_price}")
                    # for j in range(len(descriptions)):
                    #     print(f"{elements[j]}: {descriptions[j]}")
                    # Формируем сообщение
                    message = f"🚗 <b>{car_name[7:]}</b>\n<b>Цена</b>: <i>{car_price}</i>\n"
                    for j in range(len(descriptions)):
                        message += f"<b>{elements[j]}</b>: <i>{descriptions[j]}</i>\n"

                    #message += f"Фото: {src}"

                    # Отправляем фото с подписью
                    try:
                        url = f"https://api.telegram.org/bot{API_TOKEN}/sendPhoto"
                        data = {
                            "chat_id": chat_id,
                            "photo": src,
                            "caption": message,
                            "parse_mode": "HTML"
                        }
                        requests.post(url, data=data)
                    except Exception as e:
                        print(f"Ошибка при отправке фото: {e}")
                        # Если не удалось отправить фото, отправляем только текст
                        await send_message(chat_id, message)

                    # Спросить у пользователя, открывать ли следующую машину
                    result = input("Next? (yes/no): ").strip().lower()
                    if result != "yes":
                        await browser.close()
                        return

                    # Возвращаемся на страницу со списком
                    await page.go_back()
                    await page.wait_for_load_state("domcontentloaded")

                    i += 1  # Увеличиваем счетчик

                    # Если обработано 4 автомобиля, переходим на следующую страницу
                    if i == 19:
                        print(
                            f"Обработано {i} автомобилей. Переход на следующую страницу."
                        )
                        break  # Выход из цикла автомобилей

                if i == 19:
                    page_count += 1
                    await page.goto(
                        f"https://auto.drom.ru/all/page{page_count}/?minprice=100000&maxprice=200000",
                        wait_until="domcontentloaded",
                    )
                    await page.wait_for_load_state("domcontentloaded")
                    break  # Перезапускаем цикл автомобилей для новой страницы

        await asyncio.sleep(100)
        await browser.close()


if __name__ == "__main__":
    asyncio.run(main())
