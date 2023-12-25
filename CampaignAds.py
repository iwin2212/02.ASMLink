import asyncio

from playwright.async_api import Playwright, async_playwright


async def run(playwright: Playwright):
  browser = await playwright.chromium.connect_over_cdp("http://localhost:9222")
  default_context = browser.contexts[0]
  page = default_context.pages[0]

  ocid = 1262489681
  await page.goto(f"https://ads.google.com/aw/ads?ocid={ocid}&hl=en")

  pendingEle = page.locator('.status-text')
  await pendingEle.is_visible()
  # print(await pendingEle.text_content())
  await pendingEle.hover()
  appealEle = page.locator(".appeal-button")
  await appealEle.is_visible()
  # print(await appealEle.text_content())
  await appealEle.click()

async def main():
  async with async_playwright() as playwright:
    await run(playwright)
asyncio.run(main())
