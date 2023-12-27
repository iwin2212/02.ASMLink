import asyncio
import json

import pypeln as pl
from playwright.async_api import Playwright, async_playwright


async def appealGoogle(browser, ocid: int):    
    page = await browser.new_page()
    await page.goto(f"https://ads.google.com/aw/ads?ocid={ocid}&hl=en")

    # step 1: hover pending
    pendingEle = page.locator('.status-text')
    await pendingEle.is_visible()
    await pendingEle.hover()
    await pendingEle.focus()

    # step 2: click appeal button
    await page.wait_for_selector(".appeal-button")
    appealEle = page.locator(".appeal-button").get_by_text("Appeal")
    await appealEle.is_visible()
    await appealEle.click()

    # step 3: click Dispute button
    await page.wait_for_selector('material-radio-group')
    await page.click('text=Dispute decision')

    #step 4: submit
    submitBtn = page.locator('material-button.btn-yes>.content').get_by_text("Submit")
    print(submitBtn)
    await submitBtn.click()
    
    if browser is None:
      await page.close()
  
async def appealAds(ocid):
  async with async_playwright() as playwright:
    browser = await playwright.chromium.connect_over_cdp("http://localhost:9222")
    await appealGoogle(browser, ocid)

    return browser 

async def main():
  list_ocid = [1287196733,1262489681,1287027799,1287137976,1271539610,1266318633,1266376217]
  await pl.task.map(appealAds, list_ocid, workers=10)

asyncio.run(main())
