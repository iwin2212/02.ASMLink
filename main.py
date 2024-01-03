from operator import contains
from capmonstercloudclient import CapMonsterClient, ClientOptions
from capmonstercloudclient.requests import RecaptchaV2ProxylessRequest
import aiohttp
import re
from bs4 import BeautifulSoup
from datetime import datetime, timedelta
from urllib.parse import urlparse, parse_qs
import pypeln as pl
from urllib.parse import urljoin
from enum import Enum
import json
import asyncio
from urllib.parse import quote
from crawler import *

class UrlCrawler(Enum):
    Goaffpro = 'https://allpowers.goaffpro.com/login'
    Meross_Goaffpro = 'https://meross-affiliate.goaffpro.com/login'
    Shoutout = 'https://www.shoutout.global/login'
    Uppromote = 'https://af.uppromote.com/solar-power-store-canada/login'
    Linkmink = 'https://app.linkmink.com/login'
    CELLXPERT = 'https://affiliates.fiverr.com/login'
    BRAIN_STORM_FORCE = 'https://thelogocompany.net/affiliate-area'
    AFFILIATLYCOM = 'https://www.affiliatly.com/'
    POSTAFFILIATEPRO = 'https://aejuice.postaffiliatepro.com/'
    DESCRIBELY = 'https://partners.describely.ai/affiliates/login.php'
    FLOCKSOCIAL = 'https://affiliates.flocksocial.com'
    WITHBLAZE = 'https://affiliates.withblaze.app/'
    REDITUS = 'https://api.getreditus.com/auth/sign_in'
    LEADDYNO = 'leaddyno.com'
    IDEVAFFILIATE1 ='affiliate.hide-my-ip.com'
    IDEVAFFILIATE2 ='affiliate.simplybook.me'
    HASOFFERS = 'https://affiliate.vipre.com/'
    CONTADU = 'https://app.neuronwriter.com/ucp/'

    def __str__(self):
        return self.name

    @property
    def loginAPI(self):
        if self in (UrlCrawler.Goaffpro, UrlCrawler.Meross_Goaffpro):
            return 'https://api2.goaffpro.com/partner/login'
        if self is UrlCrawler.Shoutout:
            return 'https://www.shoutout.global/checklogin'        
        if self is UrlCrawler.Uppromote:
            return 'https://af.uppromote.com/solar-power-store-canada/login_aff'  
        if self is UrlCrawler.Linkmink:
            return 'https://app.linkmink.com/api/login'  
        if self is UrlCrawler.CELLXPERT:
            return 'https://fiverraffiliates.com/loginaffiliate/'
        if self is UrlCrawler.BRAIN_STORM_FORCE:
            return 'https://thelogocompany.net/affiliate-area/'

    @property
    def dataAPI(self):
        if self in (UrlCrawler.Goaffpro, UrlCrawler.Meross_Goaffpro):
            return 'https://api2.goaffpro.com/partner/sales/summary/1672506000000/1701502813931'
        if self is UrlCrawler.Shoutout:
            return 'https://www.shoutout.global/userdashboard'        
        if self is UrlCrawler.Uppromote:
            return 'https://af.uppromote.com/solar-power-store-canada/dashboard' 
        if self is UrlCrawler.Linkmink:
            return 'https://app.linkmink.com/api/login'  
        if self is UrlCrawler.CELLXPERT:
            return 'https://affiliateapi.cellxpert.com/?command=DashboardOverview'
        if self is UrlCrawler.BRAIN_STORM_FORCE:
            return 'https://thelogocompany.net/affiliate-area/'
        
    @property
    def tokenAPI(self):
        if self is UrlCrawler.Linkmink:
            return 'https://app.linkmink.com/api/v0.1.0' 
        if self is UrlCrawler.CELLXPERT:
            return 'https://fiverraffiliates.com/affiliatev2/' 

class DataCrawler:
    def __init__(self, data):
        self.data = data
        self.default_headers = {
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.7',
            'Accept-Encoding': 'gzip, deflate, br',
            'Accept-Language': 'vi-VN,vi;q=0.9,en-US;q=0.8,en;q=0.7,fr-FR;q=0.6,fr;q=0.5',
            'Content-Type': 'application/x-www-form-urlencoded',
            'Sec-Ch-Ua': '"Google Chrome";v="119", "Chromium";v="119", "Not?A_Brand";v="24"',
            'Sec-Ch-Ua-Mobile': '?0',
            'Sec-Ch-Ua-Platform': '"Windows"',
            'Sec-Fetch-Dest': 'document',
            'Sec-Fetch-Mode': 'navigate',
            'Sec-Fetch-Site': 'none',
            'Sec-Fetch-User': '?1',
            'Upgrade-Insecure-Requests': '1',
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/119.0.0.0 Safari/537.36'
        }
    # step 1: solve captcha
    async def solve_captcha(self, WEBSITE_URL, WEBSITE_KEY):
        API_KEY = "b238f538e55b7deb0da93267f61d8763"
        client_options = ClientOptions(api_key=API_KEY)
        cap_monster_client = CapMonsterClient(options=client_options)
        recaptcha2request = RecaptchaV2ProxylessRequest(
            websiteUrl= WEBSITE_URL,
            websiteKey= WEBSITE_KEY
        )
        return await cap_monster_client.solve_captcha(recaptcha2request)
    
    # step 2: Login and get authentication
    def extract_cookies_from_header(self, set_cookie_header): #Uppromote
        cookies = re.findall(r'Set-Cookie: (.*?);', set_cookie_header)
        cookies_string = "; ".join(cookies)
        return cookies_string
        
    async def getTokenFromLinkMink(self, response): #Linkmink
        data = await response.json()
        cgid = data["groups"][0]["id"]
        userID = data["userID"]
        authToken = None
        async with aiohttp.ClientSession() as session:
            headers = {
                'Cookie': response.headers.get("Set-Cookie")
            }
            async with session.get(f"{str(UrlCrawler.Linkmink.loginAPI)[:str(UrlCrawler.Linkmink.loginAPI).rfind('/')]}/users/{userID}/auth-token", headers=headers) as responseAuth:         
                if response.status == 200:
                    authToken = (await responseAuth.json())["token"] if response else ""                    
                else:
                    print(f"Error LinkMink: {response.status}")
        if authToken:
            async with aiohttp.ClientSession() as session:
                headers = {
                    'Authorization': f'Bearer {authToken}'
                }
                async with session.get(f"{UrlCrawler.Linkmink.tokenAPI}/token?cgid={cgid}", headers=headers) as responseAuth:         
                    if response.status == 200:
                        token = (await responseAuth.json())["data"]["jwt"] if response else ""
                        return token, authToken
                    else:
                        print(f"Error LinkMink: {response.status}")
        return None, None

    def extract_info_from_html(self, formatStr, page_content):
        match = re.search(formatStr, page_content)
        if match and match.group(1):
            return match.group(1)
        else:
            return None
        
    async def crawl_data_affiliatly(self, html_content):
        soup = BeautifulSoup(html_content, 'html.parser')
        unpaid_div = soup.find('div', class_='pull-left half_row')
        unpaid_value = unpaid_div.strong.text
        table = soup.find('table', class_='stats_n_orders')
        total_row = soup.find('td', string='Total:').parent
        visitors_total = total_row.find_all('td')[1].text
        orders_total = total_row.find_all('td')[2].text
        earnings_total = total_row.find_all('td')[4].text
        data_crawl = {
            'Unpaid Earnings': unpaid_value,
            'Total Visitors': visitors_total,
            'Total Orders': orders_total,
            'Total Your Earnings': earnings_total,
        }
        return data_crawl

    async def getAuthFromResponse(self, url, response):
        if url in (UrlCrawler.Goaffpro.loginAPI, UrlCrawler.Meross_Goaffpro.loginAPI):
            if response.status == 200:
                data = await response.json()
                token = data.get("access_token")
                if token:
                    return token
                else:
                    print("Authentication failed.")
            else:
                print(f"Error {response.status}: {await response.text()}")
            return None
        elif url == UrlCrawler.Shoutout.loginAPI:
            if response.status == 200:
                html_content = await response.text()
                id = self.extract_info_from_html(r'/userdashboard\?id=([a-zA-Z0-9]+)', html_content)
                if id:
                    return id
                else:
                    print("Không tìm thấy id.")
            else:
                print(f"Error {response.status}: {await response.text()}")
            return None
        elif url == UrlCrawler.Uppromote.loginAPI:
            if response.status == 302:
                cookies = response.cookies
                if cookies:
                    return self.extract_cookies_from_header(str(cookies))
                else:
                    print("Không tìm thấy token.")
                    return None, None
            else:
                print(f"Error {response.status}: {await response.text()}")
                response.raise_for_status()
                return None, None
        elif url == UrlCrawler.Linkmink.loginAPI:
            if response.status == 200:
                if response:
                    token, authToken = await self.getTokenFromLinkMink(response)
                    return token, authToken, response.headers.get("Set-Cookie")
                else:
                    print("Không tìm thấy token.")
            else:
                print(f"Error {response.status}: {await response.text()}")
                response.raise_for_status()
            return None, None, None
        elif url == UrlCrawler.CELLXPERT.loginAPI:
            affiliateApiToken = None
            loopCnt = 0
            if response.status == 302:
                if response:
                    cookies = response.headers.get("Set-Cookie")
                    while not affiliateApiToken and loopCnt < 2:
                        headers = {
                            'Cookie': cookies
                        }
                        async with aiohttp.ClientSession() as session:
                            async with session.get(str(UrlCrawler.CELLXPERT.tokenAPI), headers=headers) as responseAuth:  
                                if responseAuth.status == 200: 
                                    page_content = await responseAuth.text()
                                    affiliateApiToken = self.extract_info_from_html(r'localStorage\.setItem\("affiliateApiToken",\s*\'([^\']+)\'\)', page_content) 
                                    if affiliateApiToken:
                                        return affiliateApiToken
                                    else:
                                        cookies += "; rbzid=" + str(self.extract_info_from_html(r'seed\s*[:=]\s*["\']([^"\']+)["\']', page_content)) 
                                else:
                                    print(f"Error CELLXPERT: {responseAuth.status}") 
                        loopCnt += 1
                else:
                    print("Không tìm thấy token.")
            else:
                print(f"Error CELLXPERT {response.status}: {await response.text()}")
                response.raise_for_status()
            return None
        elif url == UrlCrawler.BRAIN_STORM_FORCE.loginAPI:
            if response.status == 302:
                if response:
                    return "; ".join(f"{k}={v.value}" for k, v in response.cookies.items())
                else:
                    print("Không tìm thấy cookies.")
            else:
                print(f"Error BRAIN_STORM_FORCE {response.status}: {await response.text()}")
                response.raise_for_status()
            return None

    async def LoginAndGetAuthAsync(self, url, payload, headers):
        async with aiohttp.ClientSession() as session:
            async with session.post(url, data=payload, headers=headers, allow_redirects=False) as response:
                return await self.getAuthFromResponse(url, response)
    
    # step 3: fetch data
    def get_first_and_last_day(self, year, month):
        if not 1 <= month <= 12:
            raise ValueError("Month must be in the range 1 to 12.")

        if month == 12:
            next_month = datetime(year + 1, 1, 1)
        else:
            next_month = datetime(year, month + 1, 1)

        last_day = next_month - timedelta(days=1)
        return datetime(year, month, 1), last_day

    def convert_to_unix_timestamp(self, dt):
        return int(dt.timestamp() * 1000)
    
    async def fetch_data(self, url, **kwargs):
        if url in (UrlCrawler.Goaffpro.value, UrlCrawler.Meross_Goaffpro.value):
            crawlUrl = f"{UrlCrawler.Goaffpro.dataAPI}?startDate={kwargs.get('startDate', '').strftime('%Y-%m-%d')}&endDate={kwargs.get('endDate', '').strftime('%Y-%m-%d')}"
            headers = {
                'Origin': urljoin(url, '/'),
                'Authorization': f'Bearer {kwargs.get("token", "")}'
            }
            async with aiohttp.ClientSession() as session:
                async with session.get(crawlUrl, headers=headers) as response:
                    data = await response.text()
                    return {
                        str(UrlCrawler.Goaffpro): data
                    } if url in (UrlCrawler.Goaffpro.value) else {
                        str(UrlCrawler.Meross_Goaffpro): data
                    }
        elif UrlCrawler.Shoutout.value in url:
            async with aiohttp.ClientSession() as session:
                async with session.get(f"{UrlCrawler.Shoutout.dataAPI}?id={kwargs.get('id', '')}") as response:            
                    if response.status == 200:
                        html_content = await response.text()
                        soup = BeautifulSoup(html_content, 'html.parser')
                        
                        total_revenue_element = soup.find(id='totalRevenueTxt')
                        return {
                            "Shoutout": {
                                "salesCommissionTxt": soup.select('.card .card-body h1.card-title')[0].get_text(strip=True),
                                "leadTxt": soup.select('.card .card-body h1.card-title')[1].get_text(strip=True),
                                "totalRevenueTxt": total_revenue_element.get_text(strip=True) if total_revenue_element is not None else None,
                                "totalCommissionTxt": soup.select('.card .card-body .col-12 h2')[1].get_text(strip=True),
                                "pendingCommissionTxt": soup.select('.card .card-body .col-12 h2')[2].get_text(strip=True)
                            }
                        }
                    else:
                        print(f"Error: {response.status}")
                        return None
        elif url == UrlCrawler.Uppromote.value:
            headers = {'Cookie': kwargs.get('cookie', '')}
            async with aiohttp.ClientSession() as session:
                async with session.get(str(UrlCrawler.Uppromote.dataAPI), headers=headers) as response:         
                    if response.status == 200:
                        html_content = await response.text()
                        soup = BeautifulSoup(html_content, 'html.parser')
                        
                        selected_elements = soup.select('#commission .panel-body__pending, #commission .panel-body__approved, #commission .panel-body__paid')
                        return {
                            "Uppromote": {label_element.text.strip(): element.text.strip() for element in selected_elements if (label_element := element.find_next(class_='my-0')) is not None}
                        }
                    else:
                        print(f"Error: {response.status}")
                        return None
        elif url == UrlCrawler.Linkmink.value:
            traffic = 0
            conversions = 0
            commissions = 0

            headers = {
                'Authorization': f'Bearer {kwargs.get("authToken", "")}',
                'Cookie': kwargs.get("cookie", "")+f';lm_auth={kwargs.get("token", "")}',
            }         
            first_day, last_day = self.get_first_and_last_day(datetime.now().year, datetime.now().month)
            async with aiohttp.ClientSession() as session:
                async with session.get(f"{UrlCrawler.Linkmink.tokenAPI}/clicks/metrics?livemode=true&min_date={self.convert_to_unix_timestamp(first_day)}&max_date={self.convert_to_unix_timestamp(last_day)}&timezone=Asia%2FBangkok", headers=headers) as response:         
                    if response.status == 200:
                        result = await response.json()
                        traffic = result["metrics"]
                    else:
                        print(f"Error: {response.status} -  {await response.text()}")
                    
            async with aiohttp.ClientSession() as session:
                async with session.get(f"{UrlCrawler.Linkmink.tokenAPI}/conversions/metrics?livemode=true&min_date={self.convert_to_unix_timestamp(first_day)}&max_date={self.convert_to_unix_timestamp(last_day)}&withCredentials=true&timezone=Asia%2FBangkok", headers=headers) as response:         
                    if response.status == 200:
                        result = await response.json()
                        conversions = result["metrics"]
                    else:
                        print(f"Error: {response.status} - {await response.text()}")
                    
            async with aiohttp.ClientSession() as session:
                async with session.get(f"{UrlCrawler.Linkmink.tokenAPI}/commissions/metrics?livemode=true&min_date={self.convert_to_unix_timestamp(first_day)}&max_date={self.convert_to_unix_timestamp(last_day)}&timezone=Asia%2FBangkok", headers=headers) as response:         
                    if response.status == 200:
                        result = await response.json()
                        commissions = result["metrics"]
                    else:
                        print(f"Error: {response.status} -  {await response.text()}")
            return {
                "Linkmink":{
                    "traffic": traffic,
                    "conversions": conversions, 
                    "commissions": commissions
                }
            }
        elif url == UrlCrawler.CELLXPERT.value:
            headers = {
                'affiliate_url': 'Fiverr',
                'Authorization': f"Bearer {kwargs.get('token', '')}"
            }
            first_day, last_day = self.get_first_and_last_day(datetime.now().year, datetime.now().month)
            async with aiohttp.ClientSession() as session:
                async with session.get(f"{UrlCrawler.CELLXPERT.dataAPI}&enddate={quote(last_day.strftime('%m/%d/%Y'))}&startdate={quote(first_day.strftime('%m/%d/%Y'))}&uniqueId=793046888", headers=headers) as response:         
                    if response.status == 200:
                        result = await response.json()
                        return {
                            "CELLXPERT": result
                        }
                    else:
                        print(f"Error CELLXPERT {response.status}: {await response.text()}")
                        return None
        elif url == UrlCrawler.BRAIN_STORM_FORCE.value:
            headers = {
                'Cookie':kwargs.get('cookie', '')
            }
            first_day, last_day = self.get_first_and_last_day(datetime.now().year, datetime.now().month)
            async with aiohttp.ClientSession() as session:
                async with session.get(str(UrlCrawler.BRAIN_STORM_FORCE.dataAPI), headers=headers) as response:
                    if response.status == 200:
                        html_content = await response.text()
                        soup = BeautifulSoup(html_content, 'html.parser')
                        keys = soup.select(".text-sm.leading-5.font-medium.text-gray-500.truncate")
                        values = soup.select(".items-baseline div")
                        return {
                            "BRAIN_STORM_FORCE": {key.text.strip(): value.text.strip() for key, value in zip(keys, values)}
                        }
                    else:
                        print(f"Error BRAIN_STORM_FORCE {response.status}: {await response.text()}")
                        return None
        
    # Crawl data func
    async def crawl_data(self, args):
        if len(args)<=0:
            print("Insufficient number of arguments.")
            return None
        url, email, password = args
        if url in (UrlCrawler.Goaffpro.value, UrlCrawler.Meross_Goaffpro.value):
            WEBSITE_KEY = '6Lf_jsQUAAAAAOLW40PpDXgZQDIjjnGldAE1fhYr'
            res = await self.solve_captcha(url,WEBSITE_KEY)
            payload = {
                "email": email,
                "password": password,
                "partner_portal_subdomain": "allpowers.goaffpro.com",
                "recaptcha_response": res["gRecaptchaResponse"]
            }
            headers = {
                'Origin': urljoin(url, '/')
            }
            
            token = await self.LoginAndGetAuthAsync(UrlCrawler.Meross_Goaffpro.loginAPI, payload, headers)
            if token:
                first_day, last_day = self.get_first_and_last_day(datetime.now().year, datetime.now().month)
                data = await self.fetch_data(url, startDate=first_day, endDate=last_day, token=token)                
                return data
            else:
                print("Failed to obtain token.")
                return None
        elif UrlCrawler.Shoutout.value in url:
            WEBSITE_KEY = '6LfvfrEUAAAAAPg5Dt1q3UsmCwD_Z5oELX4s95eB'
            encryptedID = parse_qs(urlparse(url).query)
            res = await self.solve_captcha(url,WEBSITE_KEY)
            payload = {
                "email": email,
                "password": password,
                "g-recaptcha-response": res["gRecaptchaResponse"],
                "encryptedID": encryptedID["id"][0]
            }
            headers = {
                'Origin': urljoin(url, '/')
            }                
            id = await self.LoginAndGetAuthAsync(UrlCrawler.Shoutout.loginAPI, payload, headers)
            if id:
                data = await self.fetch_data(url, id=id)
                return data
            else:
                print("Failed to obtain ID.")
                return None
        elif url == UrlCrawler.Uppromote.value:
            WEBSITE_KEY = '6LcfFqkaAAAAAODkHHT2DLE7UBeSbf7kVCdBkTQE'
            res = await self.solve_captcha(url, WEBSITE_KEY)
            payload = {
                "_token": "5xhC3w0BB9Cezh7fhtZJg5YaHJvyInW5AC4qy8Mi",
                "shop_id": "80375",
                "email": email,
                "password": password,
                "g-recaptcha-response": res["gRecaptchaResponse"]
            }
            headers = {}

            cookie = await self.LoginAndGetAuthAsync(UrlCrawler.Uppromote.loginAPI, payload, headers)

            return await self.fetch_data(url, cookie=cookie)
        elif url == UrlCrawler.Linkmink.value:
            payload = {
                "username": email,
                "password": password
            }
            headers = {}

            result = await self.LoginAndGetAuthAsync(UrlCrawler.Linkmink.loginAPI, payload, headers)
            if result and len(result) == 3:
                token, authToken, cookie = result
                return await self.fetch_data(url, token=token, authToken=authToken, cookie=cookie)
        elif url == UrlCrawler.CELLXPERT.value:
            payload = {
                "action": "affiliates_login",
                "token": "",
                "errorurl": "https://affiliates.fiverr.com/",
                "command": "logon",
                "user": email,
                "password": password,
                "rememberme": "on"
            }

            headers = {}

            token = await self.LoginAndGetAuthAsync(UrlCrawler.CELLXPERT.loginAPI, payload, headers)
            if token:
                return await self.fetch_data(url, token=token)
        elif url == UrlCrawler.BRAIN_STORM_FORCE.value:
            payload = {
                "affwp_user_login": email,
                "affwp_user_pass": password,
                "affwp_user_remember": "1",
                "affwp_redirect": "",
                "affwp_login_nonce": "6ea01909f0",
                "affwp_action": "user_login"
            }
            headers = {}
            cookie = await self.LoginAndGetAuthAsync(UrlCrawler.BRAIN_STORM_FORCE.loginAPI, payload, headers)
            if cookie:
                return await self.fetch_data(url, cookie=cookie)
        elif UrlCrawler.AFFILIATLYCOM.value in url:
            crawler = AffiliatlyComCrawler(*args)
            return await crawler.crawl()
        elif UrlCrawler.DESCRIBELY.value in url or UrlCrawler.POSTAFFILIATEPRO.value in url:
            crawler = DescribelyAndPostaffiliateproCrawler(*args)
            return await crawler.crawl()
        elif UrlCrawler.WITHBLAZE.value in url or UrlCrawler.FLOCKSOCIAL.value in url:
            crawler = WithblazeAndFlocksocialCrawler(*args)
            return await crawler.crawl()
        elif UrlCrawler.REDITUS.value == url:
            crawler = ReditusCrawler(*args)
            return await crawler.crawl()
        elif UrlCrawler.LEADDYNO.value in url:
            crawler = LeaddynoCrawler(*args)
            return await crawler.crawl()
        elif UrlCrawler.IDEVAFFILIATE1.value in url or UrlCrawler.IDEVAFFILIATE2.value in url:
            crawler = DevaffiliateCrawler(*args)
            return await crawler.crawl()
        elif UrlCrawler.HASOFFERS.value == url:
            crawler = HasoffersCrawler(*args)
            return await crawler.crawl()
        elif UrlCrawler.CONTADU.value == url:
            crawler = ContaduCrawler(*args)
            return await crawler.crawl()
        
    async def crawl(self):
        result = await pl.task.map(self.crawl_data, self.data, workers=100)
        print(json.dumps(result, indent=4))

data = [
    # ("https://allpowers.goaffpro.com/login", "natashacook371sdas@gmail.com", "Qxwg0CN09v"),
    # ("https://meross-affiliate.goaffpro.com/login", "natashacook371sdas@gmail.com", "Qxwg0CN09v"),
    # ("https://www.shoutout.global/login?id=22wbe", "natashacook371sdas@gmail.com", "Qxwg0CN09v"), 
    # ("https://www.shoutout.global/login?id=obbi7", "teamasmads@gmail.com", "E9vQRQmPG!a.7m6"),
    # ("https://af.uppromote.com/solar-power-store-canada/login", "teamasmads@gmail.com", "2N*G5k$7ux5j2!F"),
    # ('https://app.linkmink.com/login', 'evenelson380df@gmail.com', 'jfLo3HlVelSxkKQ'),
    # ('https://affiliates.fiverr.com/login', 'beckyross766re@gmail.com', 'Niyj6MU30j'),
    # ('https://thelogocompany.net/affiliate-area', 'evenelson380df@gmail.com', 'xL&i172j@]'),
    
    # ('https://www.affiliatly.com/af-1031650/affiliate.panel', 'teamasmads@gmail.com', '2N*G5k$7ux5j2!F'),
    # ('https://www.affiliatly.com/af-1040475/affiliate.panel', 'beckyanderson23g@gmail.com', '9qWWo95F31Nq@'),
    # ('https://aejuice.postaffiliatepro.com/affiliates/', 'charlotteflores549sd@gmail.com', 'Utuw1ZR05b'),
    # ('https://partners.describely.ai/affiliates/login.php', 'emilymurphy965df@gmail.com', 'heqadqlTk8Z601T'),
    # ('https://affiliates.withblaze.app/', 'maddietaylor376cv@gmail.com', 'Aceu9YO60m'),
    # ('https://affiliates.flocksocial.com', 'beckyanderson23g@gmail.com', 'hI8p63uW90a9'), link này lỗi
    
    ('https://api.getreditus.com/auth/sign_in', 'alishacooper125we@gmail.com', 'sB"K3??9^8;n'),
    ('https://api.getreditus.com/auth/sign_in', 'staakerole@gmail.com', 'QqHzAXjVR8#uBBN'),
    ('https://cramly.leaddyno.com/sso', 'teamasmads@gmail.com', 'yqZWRKe6hrYmS4u'),
    ('https://tradelle.leaddyno.com/sso', 'teamasmads@gmail.com', '2fijD4FNfM4Z@pj'),
    ('https://affiliate.hide-my-ip.com/login.php', 'beckyanderson23g', 'CqA5v9BvI6J0'),
    ('https://affiliate.simplybook.me/login.php', 'emilymurphy965df', 'L4AYLVa97S'),
    ('https://affiliate.vipre.com/', 'evenelson380df@gmail.com', 'A61yIU8g4!f)'),
    ('https://affiliate.vipre.com/', 'alishacooper125we@gmail.com', 'J9figOCIfbMICXB'),
    ('https://affiliate.vipre.com/', 'asmlongle@gmail.com', 'tj5kLv2dNmZgZ!f'),
    ('https://app.neuronwriter.com/ucp/', 'eleanorlewis676rsdf@gmail.com', 'C9xvPC$SCcU;6~V'),
]
async def main():
    crawler = DataCrawler(data)
    await crawler.crawl()
    
# Chạy chương trình chính
if __name__ == "__main__":
    asyncio.run(main())