import asyncio
from socket import timeout
from urllib.parse import parse_qs, urlparse

import pypeln as pl
from playwright.async_api import Playwright, async_playwright

list_ocid = [1287196733,1262489681,1287027799,1287137976,1271539610,1266318633,1266376217]

async def appealGoogle(page):  
    if list_ocid is None or len(list_ocid) == 0:
      await page.close()
    else:
      ocid = list_ocid.pop()
      await page.goto(f"https://ads.google.com/aw/ads?ocid={ocid}&hl=en")
      await page.wait_for_selector('.status-text', state='visible')
      pendingEles = await page.locator('.status-text').all()
      for i, pendingEle in enumerate(pendingEles):
        # step 1: hover pending
        await pendingEle.hover()
        await pendingEle.focus()
        try:
          # step 2: click appeal button
          await page.wait_for_selector(".appeal-button", timeout=1000)
          appealEle = page.locator(".appeal-button").get_by_text("Appeal")
          await appealEle.is_visible()
          await appealEle.click()

          # step 3: click Dispute button
          await page.wait_for_selector('material-radio-group')
          await page.click('text=Dispute decision')

          #step 4: submit
          submitBtn = page.locator('material-button.btn-yes>.content').get_by_text("Submit")
          await submitBtn.click()
          print('Ocid: {}: Campaign {} appeal success!'.format(ocid, i+1))
        except:
          print('Ocid: {}: Campaign {} has been appealed!'.format(ocid, i+1))
      return await appealGoogle(page)
  
async def main():
  async with async_playwright() as playwright:
    try:
      browser = await playwright.chromium.connect_over_cdp("http://localhost:9222")
      default_context = browser.contexts[0]
      page = await default_context.new_page()
      await appealGoogle(page)
      print("Done!!!")
    except Exception as ex:
      print(f"(Error: {ex}")
asyncio.run(main())
