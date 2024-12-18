import asyncio
from playwright.async_api import async_playwright
from fake_useragent import FakeUserAgent
import json
from pathlib import Path


async def main():
    async with async_playwright() as p:

        # Запускаем браузер в фоновом режиме
        browser = await p.chromium.launch(
            headless=False, args=["--disable-blink-features=AutomationControlled"]
        )  # Установите headless=True

        user_agent = FakeUserAgent().random
        await browser.new_context(user_agent=user_agent)
        context = await browser.new_context()
        await context.add_cookies(json.loads(Path("cookies.json").read_text()))
        page = await context.new_page()

        # high_price_car = int(input("High price: "))
        # low_price_car = int(input("Low price: "))
        page_count = 1
        await page.goto(
            f"https://auto.drom.ru/all/page{page_count}/?minprice=100000&maxprice=200000",
            wait_until="domcontentloaded",
        )

        while True:  # Бесконечный цикл для перехода по страницам
            while True:  # Цикл для автомобилей на текущей странице
                car_page = page.locator(
                    "//html/body/div[2]/div[4]/div[1]/div[1]/div[5]/div/div[1]/div/div[2]/div[1]/a/h3"
                )
                car_count = await car_page.count()
                print(f"Найдено автомобилей: {car_count}")

                i = 0
                while i < car_count:  # Вложенный цикл по автомобилям
                    print(f"\nОткрываем автомобиль №{i + 1}")
                    car = car_page.nth(i)
                    await car.click()  # Открываем карточку автомобиля
                    await page.wait_for_load_state("domcontentloaded")

                    # Сбор информации о машине
                    car_name_locator = page.locator(
                        "//html/body/div[2]/div[3]/div[2]/h1/span"
                    )
                    car_price_locator = page.locator(
                        "//html/body/div[2]/div[4]/div[1]/div[1]/div[2]/div[2]/div[1]/div/div[1]"
                    )

                    car_name = (
                        await car_name_locator.text_content()
                        if await car_name_locator.count() > 0
                        else "Неизвестно"
                    )
                    car_price = (
                        await car_price_locator.text_content()
                        if await car_price_locator.count() > 0
                        else "Неизвестно"
                    )

                    # Атрибуты и значения
                    elements_car_locator = page.locator(
                        "//html/body/div[2]/div[4]/div[1]/div[1]/div[2]/div[2]/div/table/tbody/tr/th"
                    )
                    descriptions_car_locator = page.locator(
                        "//html/body/div[2]/div[4]/div[1]/div[1]/div[2]/div[2]/div[2]/table/tbody/tr/td"
                    )

                    elements = await elements_car_locator.all_text_contents()
                    descriptions = await descriptions_car_locator.all_text_contents()
                    if len(descriptions) > 2:
                        descriptions.pop(2)  # Удаляем ненужный элемент

                    # Проверяем наличие фото
                    try:
                        photo_car = page.locator(
                            "//html/body/div[2]/div[4]/div[1]/div[1]/div[2]/div[1]/div[1]/div/div/div[1]/a/div/div/div/div/img"
                        )
                        if await photo_car.count() > 0:
                            src = await photo_car.get_attribute("src")
                            print(f"Фото автомобиля: {src}")
                        else:
                            print("https://xn--90aha1bhcc.xn--p1ai/img/placeholder.png")
                    except Exception as e:
                        print(f"Ошибка при получении фото: {e}")

                    # Вывод информации
                    print(f"Название: {car_name[7:]}")
                    print(f"Цена: {car_price}")
                    for j in range(len(descriptions)):
                        print(f"{elements[j]}: {descriptions[j]}")

                    # Спросить у пользователя, открывать ли следующую машину
                    result = input("Другую машину? (yes/no): ").strip().lower()
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
