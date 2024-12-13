import asyncio
from playwright.async_api import async_playwright
from fake_useragent import FakeUserAgent
import json
from pathlib import Path

async def main():
    async with async_playwright() as p:

        # Запускаем браузер в фоновом режиме
        browser = await p.chromium.launch(
            headless=False,
            args=['--disable-blink-features=AutomationControlled']
        ) # Установите headless=True

        user_agent = FakeUserAgent().random
        await browser.new_context(user_agent=user_agent)
        context = await browser.new_context()
        await context.add_cookies(json.loads(Path("cookies.json").read_text()))
        page = await context.new_page()
        await page.goto('https://auto.drom.ru/all/?minprice=400000&maxprice=500000', wait_until='domcontentloaded')


        elements = page.locator('//html/body/div[2]/div[4]/div[1]/div[1]/div[5]/div/div[1]/div/div[2]/div[1]/a/h3')
        elements2 = page.locator('//html/body/div[2]/div[4]/div[1]/div[1]/div[5]/div/div[1]/div/div[2]/div[2]/span[1]')
        elements3 = page.locator('//html/body/div[2]/div[4]/div[1]/div[1]/div[5]/div/div[1]/div/div[2]/div[2]/span[3]')
        elements4 = page.locator('//html/body/div[2]/div[4]/div[1]/div[1]/div[5]/div/div[1]/div/div[2]/div[2]/span[5]')
        elements5 = page.locator('//html/body/div[2]/div[4]/div[1]/div[1]/div[5]/div/div[1]/div/div[3]/div[1]/div/div[1]/span/span')

        name_car = await elements.all_inner_texts()
        motor_car = await elements2.all_inner_texts()
        gearbox_car = await elements3.all_inner_texts()
        total_km_car = await elements4.all_inner_texts()
        price_car = await elements5.all_inner_texts()

        # Check for mismatched lengths
        min_length = min(len(name_car), len(motor_car), len(gearbox_car), len(total_km_car), len(price_car))

        # Print the collected data
        for number_car in range(min_length):
            print(f"Название машины: {name_car[number_car]}, Мотор: {motor_car[number_car]} Коробка передач: {gearbox_car[number_car]} Пробег: {total_km_car[number_car]}, Цена: {price_car[number_car]}, Фото: None")

        await browser.close()

if __name__ == '__main__':
    asyncio.run(main())

