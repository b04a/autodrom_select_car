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
        await page.goto('https://auto.drom.ru/all/?minprice=100000&maxprice=200000', wait_until='domcontentloaded')

        car_page = page.locator('//html/body/div[2]/div[4]/div[1]/div[1]/div[5]/div/div[1]/div[1]')
        await car_page.click()

        #full info about car
        car_name_locator = page.locator('//html/body/div[2]/div[3]/div[2]/h1/span')
        car_name = await car_name_locator.text_content()

        car_price_locator = page.locator('//html/body/div[2]/div[4]/div[1]/div[1]/div[2]/div[2]/div[1]/div/div[1]')
        car_price = await car_price_locator.text_content()

        #name attributes
        elements_car_locator = page.locator("//html/body/div[2]/div[4]/div[1]/div[1]/div[2]/div[2]/div/table/tbody/tr/th")
        #
        #data by attributes
        descriptions_car_locator = page.locator("//html/body/div[2]/div[4]/div[1]/div[1]/div[2]/div[2]/div[2]/table/tbody/tr/td")
        #
        elements = await elements_car_locator.all_text_contents()
        descriptions = await descriptions_car_locator.all_text_contents()
        descriptions.pop(2)

        for i in range(len(descriptions)):
            print(elements[i], descriptions[i])

        await asyncio.sleep(10000)
        await browser.close()

if __name__ == '__main__':
    asyncio.run(main())