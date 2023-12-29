import asyncio
import json

import pypeln as pl
from playwright.async_api import Playwright, async_playwright

list_ocid = [1287196733,1262489681,1287027799,1287137976,1271539610,1266318633,1266376217]
# list_ocid = [1266318633]

async def appealGoogle(page):  
  if not list_ocid: return None

  id = list_ocid.pop()
  await page.goto(f"https://ads.google.com/aw/ads?ocid={id}&hl=en")

  pendingEles = await page.locator('.status-text').all()
  for pendingEle in pendingEles:
    # step 1: hover pending
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
    await submitBtn.click()
    
    await page.close()
    return id
  
async def main():
  async with async_playwright() as playwright:
    browser = await playwright.chromium.connect_over_cdp("http://localhost:9222")
    default_context = browser.contexts[0]

    for i in range(0, len(list_ocid), 10):
      batch = list_ocid[i:i + 10]
      for ocid in batch:
        await default_context.new_page()

      result = await pl.task.map(appealGoogle, default_context.pages, workers=10)
      print(json.dumps(result, indent=4))

asyncio.run(main())
