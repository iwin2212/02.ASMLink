import asyncio
import json
import re
from datetime import datetime, timedelta
from enum import Enum
from urllib.parse import parse_qs, quote, urljoin, urlparse

import aiohttp
import pypeln as pl
from bs4 import BeautifulSoup
from capmonstercloudclient import CapMonsterClient, ClientOptions
from capmonstercloudclient.requests import RecaptchaV2ProxylessRequest


class Crawler:
    def __init__(self, url, username, password) -> None:
        self.url = url
        self.username = username
        self.password = password


class DescribelyAndPostaffiliateproCrawler(Crawler):
    def __init__(self, url, username, password) -> None:
        super().__init__(url, username, password)

    async def crawl(self):
        idx = self.url.index("/affiliates")
        self.url = self.url[:idx]

        async def extract_cookie(cookie_string):
            idx1 = cookie_string.index("=")
            idx2 = cookie_string.index(";")

            cookie_string = cookie_string[idx1 + 1 : idx2]
            return cookie_string

        async with aiohttp.ClientSession() as session:
            url = f"{self.url}/affiliates/login.php"
            response0 = await session.get(url, headers={})
            signup_pap_sid = response0.cookies.get("signup_pap_sid")
            signup_pap_sid = str(signup_pap_sid)
            signup_pap_sid = await extract_cookie(signup_pap_sid)

            headers = {}
            headers["cookie"] = f"gpf_language=en-US; signup_pap_sid={signup_pap_sid}"

            json_data = {
                "C": "Gpf_Rpc_Server",
                "M": "run",
                "requests": [
                    {"C": "Gpf_Rpc_Server", "M": "syncTime", "offset": "54000000"},
                    {
                        "C": "Gpf_Templates_TemplateService",
                        "M": "getTemplate",
                        "templateName": "window_move_panel",
                    },
                    {
                        "C": "Gpf_Templates_TemplateService",
                        "M": "getTemplate",
                        "templateName": "context_menu",
                    },
                    {
                        "C": "Gpf_Templates_TemplateService",
                        "M": "getTemplate",
                        "templateName": "window_header_refresh",
                    },
                    {
                        "C": "Gpf_Templates_TemplateService",
                        "M": "getTemplate",
                        "templateName": "item",
                    },
                    {
                        "C": "Gpf_Templates_TemplateService",
                        "M": "getTemplate",
                        "templateName": "single_content_panel",
                    },
                    {
                        "C": "Gpf_Templates_TemplateService",
                        "M": "getTemplate",
                        "templateName": "form_field_checkbox",
                    },
                    {
                        "C": "Gpf_Templates_TemplateService",
                        "M": "getTemplate",
                        "templateName": "login_annotation",
                    },
                ],
                "S": signup_pap_sid,
            }
            form_data = {"D": json.dumps(json_data)}
            url_post = f"{self.url}/scripts/server.php"
            response0 = await session.post(url_post, data=form_data, headers=headers)
            headers = {}
            headers["cookie"] = f"gpf_language=en-US; signup_pap_sid={signup_pap_sid}"

            json_data = {
                "C": "Gpf_Rpc_Server",
                "M": "run",
                "requests": [
                    {
                        "C": "Gpf_Auth_Service",
                        "M": "authenticate",
                        "fields": [
                            ["name", "value"],
                            ["Id", ""],
                            ["username", self.username],
                            ["password", self.password],
                            ["twofactor_token", ""],
                            ["rememberMe", "N"],
                            ["language", "en-US"],
                            ["roleType", "A"],
                        ],
                    }
                ],
                "S": signup_pap_sid,
            }

            form_data = {"D": json.dumps(json_data)}
            response0 = await session.post(url_post, data=form_data, headers=headers)
            # isSuccess = await response0.json()

            affiliates_pap_sid = response0.cookies.get("affiliates_pap_sid")
            affiliates_pap_sid = str(affiliates_pap_sid)
            affiliates_pap_sid = await extract_cookie(affiliates_pap_sid)

            headers = {}
            headers[
                "cookie"
            ] = f"gpf_language=en-US; signup_pap_sid={signup_pap_sid}; affiliates_pap_sid={affiliates_pap_sid}"
            url = f"{self.url}/affiliates/panel.php"
            response0 = await session.get(url, headers=headers)

            # Sau đó request theo trình tự này, thay đổi headers sau khi lấy được affiliates_pap_sid
            json_data = {
                "C": "Gpf_Rpc_Server",
                "M": "run",
                "requests": [
                    {"C": "Gpf_Rpc_Server", "M": "syncTime", "offset": "54000000"},
                    {
                        "C": "Gpf_Templates_TemplateService",
                        "M": "getTemplate",
                        "templateName": "main_header",
                    },
                    {
                        "C": "Gpf_Templates_TemplateService",
                        "M": "getTemplate",
                        "templateName": "calendar",
                    },
                    {
                        "C": "Gpf_Templates_TemplateService",
                        "M": "getTemplate",
                        "templateName": "date_preset_panel",
                    },
                    {
                        "C": "Gpf_Templates_TemplateService",
                        "M": "getTemplate",
                        "templateName": "custom_date_panel",
                    },
                    {
                        "C": "Gpf_Templates_TemplateService",
                        "M": "getTemplate",
                        "templateName": "date_range_filter_field",
                    },
                    {"C": "Pap_Affiliates_MainPanelHeader", "M": "load"},
                    {
                        "C": "Gpf_Templates_TemplateService",
                        "M": "getTemplate",
                        "templateName": "tooltip_popup",
                    },
                    {
                        "C": "Gpf_Templates_TemplateService",
                        "M": "getTemplate",
                        "templateName": "form_field",
                    },
                    {
                        "C": "Gpf_Templates_TemplateService",
                        "M": "getTemplate",
                        "templateName": "affiliate_manager",
                    },
                    {
                        "C": "Gpf_Db_Table_FormFields",
                        "M": "getTranslatedFields",
                        "formId": "merchantForm",
                        "status": "M,O,R",
                    },
                    {
                        "C": "Gpf_Templates_TemplateService",
                        "M": "getTemplate",
                        "templateName": "data_field",
                    },
                    {
                        "C": "Gpf_Templates_TemplateService",
                        "M": "getTemplate",
                        "templateName": "news_content",
                    },
                    {
                        "C": "Gpf_Templates_TemplateService",
                        "M": "getTemplate",
                        "templateName": "simple_icon_object",
                    },
                    {
                        "C": "Pap_Affiliates_MerchantInfo",
                        "M": "load",
                        "fields": [["name", "value"], ["Id", ""]],
                    },
                    {"C": "Pap_Affiliates_Reports_PeriodStats", "M": "load"},
                    {"C": "Pap_Common_NewsManager", "M": "loadUnread"},
                ],
                "S": affiliates_pap_sid,
            }
            form_data = {"D": json.dumps(json_data)}
            response0 = await session.post(url_post, headers=headers, data=form_data)
            # 2
            json_data = {
                "C": "Gpf_Rpc_Server",
                "M": "run",
                "requests": [
                    {"C": "Pap_Common_NewsManager", "M": "load"},
                    {
                        "C": "Pap_Common_Reports_StatisticsBaseNew",
                        "M": "loadData",
                        "filters": [
                            ["datetime", "DP", "L7D"],
                            ["groupBy", "=", "day"],
                            ["dataType1", "=", "commission"],
                            ["dataStatus1", "=", "A"],
                            ["dataPStatus1", "=", ""],
                            ["dataType2", "=", "commission"],
                            ["dataStatus2", "=", "A"],
                            ["dataPStatus2", "=", "P"],
                            ["dataType3", "=", "commission"],
                            ["dataStatus3", "=", "P"],
                            ["dataPStatus3", "=", ""],
                        ],
                    },
                ],
                "S": affiliates_pap_sid,
            }
            form_data = {"D": json.dumps(json_data)}
            response0 = await session.post(url_post, headers=headers, data=form_data)
            # 3
            json_data = {
                "C": "Gpf_Rpc_Server",
                "M": "run",
                "requests": [
                    {
                        "C": "Gpf_Templates_TemplateService",
                        "M": "getAllMissingTemplates",
                        "templateName": "",
                        "loadedTemplates": ",loading_indicator,main,button,loading_template,breadcrumbs,icon_button,main_menu,menu_entry,menu_section,sub_menu_section,system_menu,window,window_move_panel,window_left,context_menu,window_header,window_header_refresh,window_bottom_left,window_empty_content,item,single_content_panel,home,link_button,main_header,calendar,date_preset_panel,custom_date_panel,date_range_filter_field,tooltip_popup,form_field,affiliate_manager,data_field,news_content,simple_icon_object",
                        "templatesCount": 50,
                    }
                ],
                "S": affiliates_pap_sid,
            }
            form_data = {"D": json.dumps(json_data)}
            response0 = await session.post(url_post, headers=headers, data=form_data)
            # Sau đó request theo trình tự đến Report
            json_data = {
                "C": "Gpf_Rpc_Server",
                "M": "run",
                "requests": [
                    {
                        "C": "Gpf_Db_Table_Filters",
                        "M": "getDefaultFilter",
                        "data": [["name", "value"], ["filterType", "trends_report"]],
                    },
                    {
                        "C": "Gpf_Db_Table_Filters",
                        "M": "get",
                        "filterType": "trends_report",
                    },
                    {
                        "C": "Gpf_DateTime_Range",
                        "M": "loadDateRangeFromPreset",
                        "datePreset": "L30D",
                    },
                    {
                        "C": "Pap_Affiliates_Reports_TrendsReport",
                        "M": "loadDefaultDataTypes",
                    },
                    {"C": "Pap_Affiliates_Reports_TrendsReport", "M": "loadDataTypes"},
                    {
                        "C": "Pap_Common_Campaign_CampaignForAffiliateTransactionsRichListBox",
                        "M": "load",
                        "clicks": "Y",
                        "from": 0,
                        "rowsPerPage": 20,
                        "maxCachedCount": 500,
                        "id": "cachedRequest",
                    },
                    {
                        "C": "Pap_Merchants_Campaign_AffChannelSearchRichListBox",
                        "M": "load",
                        "from": 0,
                        "rowsPerPage": 20,
                        "maxCachedCount": 500,
                        "id": "cachedRequest",
                        "userid": "",
                    },
                    {
                        "C": "Pap_Common_Banner_BannerForAffiliateStatsRichListBox",
                        "M": "load",
                        "from": 0,
                        "rowsPerPage": 20,
                        "maxCachedCount": 500,
                        "id": "cachedRequest",
                    },
                    {
                        "C": "Pap_Affiliates_Promo_DestinationUrlRichListBox",
                        "M": "load",
                        "from": 0,
                        "rowsPerPage": 20,
                        "maxCachedCount": 500,
                        "id": "cachedRequest",
                    },
                    {
                        "C": "Pap_Affiliates_Reports_TrendsReport",
                        "M": "loadData",
                        "isInitRequest": "Y",
                        "filterType": "trends_report",
                        "filters": [
                            ["datetime", "DP", "L30D"],
                            ["rpc", "=", "Y"],
                            ["groupBy", "=", "day"],
                            ["dataType1", "=", "saleCount"],
                            ["dataType2", "=", "_item_none_"],
                        ],
                    },
                ],
                "S": affiliates_pap_sid,
            }
            form_data = {"D": json.dumps(json_data)}
            response0 = await session.post(url_post, headers=headers, data=form_data)
            # 2
            json_data = {
                "C": "Gpf_Rpc_Server",
                "M": "run",
                "requests": [
                    {
                        "C": "Pap_Affiliates_Reports_TrendsReportWidget",
                        "M": "load",
                        "isInitRequest": "Y",
                        "filterType": "trends_report",
                        "filters": [["datetime", "DP", "L30D"]],
                    },
                    {
                        "C": "Pap_Stats_TransactionTypes",
                        "M": "getActionTypes",
                        "filters": [["datetime", "DP", "L30D"]],
                    },
                ],
                "S": affiliates_pap_sid,
            }
            form_data = {"D": json.dumps(json_data)}
            response0 = await session.post(url_post, headers=headers, data=form_data)

            def clean_html(html_content):
                cleaned_html = html_content.replace("\\t", "").replace("\\n", "")
                cleaned_html = (
                    cleaned_html.replace("\/", "").replace("\\", "").replace("  ", " ")
                )
                return cleaned_html

            # All time report
            json_data = {
                "C": "Gpf_Rpc_Server",
                "M": "run",
                "requests": [
                    {
                        "C": "Pap_Affiliates_Reports_TrendsReportWidget",
                        "M": "load",
                        "isInitRequest": "Y",
                        "filterType": "trends_report",
                    },
                    {"C": "Pap_Stats_TransactionTypes", "M": "getActionTypes"},
                ],
                "S": affiliates_pap_sid,
            }
            form_data = {"D": json.dumps(json_data)}
            response_html_1 = await session.post(
                url_post, headers=headers, data=form_data
            )
            # Crawl data
            cleaned_html_1 = clean_html(await response_html_1.text())
            soup = BeautifulSoup(cleaned_html_1, "html.parser")
            # # Lấy thông tin cho từng class 'row'
            rows = soup.find_all("div", class_="row")
            data_crawl = {}
            # Lặp qua từng dòng và lấy thông tin
            row1 = rows[1].text.replace("\u200e", "").strip()
            # Get index of Clicks , All clicks , CTR , Totals , Commissions
            clicks_idx = row1.index("Clicks")
            totals_idx = row1.index("Totals")
            blank_idx = row1.index(" ")
            # Hard core with string
            # Đã lấy được value clicks
            string_clicks = row1[clicks_idx:blank_idx]  # string clicks
            value_clicks = string_clicks[string_clicks.index("s") + 1 :]
            data_crawl["Clicks"] = value_clicks
            # value totals
            string_totals = row1[totals_idx:]  # split string to get data Totals
            dollar_idx = string_totals.index("$")
            commissions_idx = string_totals.index("Commissions")
            value_totals = string_totals[dollar_idx:commissions_idx]
            data_crawl["Totals"] = value_totals
            # All time Sales
            json_data = {
                "C": "Gpf_Rpc_Server",
                "M": "run",
                "requests": [
                    {
                        "C": "Pap_Affiliates_Reports_TrendsReportActionWidget",
                        "M": "load",
                        "filters": [["action", "E", "S"]],
                    }
                ],
                "S": affiliates_pap_sid,
            }
            form_data = {"D": json.dumps(json_data)}
            response_html_2 = await session.post(
                url_post, headers=headers, data=form_data
            )
            # Crawl data
            cleaned_html_2 = clean_html(await response_html_2.text())
            soup = BeautifulSoup(cleaned_html_2, "html.parser")
            rows = soup.find_all("div", class_="row")
            row0 = rows[0].text.replace("\u200e", "").strip()
            sales_idx = row0.index("Sales")
            fixed_idx = row0.index("Fixed")
            dollar_idx = row0.index("$")
            value_sale_1 = row0[:sales_idx]
            value_sale_2 = row0[dollar_idx:fixed_idx].strip()
            data_crawl["Sales"] = [value_sale_1, value_sale_2]
            return data_crawl


class UrlCrawler(Enum):
    Goaffpro = "https://allpowers.goaffpro.com/login"
    Meross_Goaffpro = "https://meross-affiliate.goaffpro.com/login"
    Shoutout = "https://www.shoutout.global/login"
    Uppromote = "https://af.uppromote.com/solar-power-store-canada/login"
    Linkmink = "https://app.linkmink.com/login"
    CELLXPERT = "https://affiliates.fiverr.com/login"
    BRAIN_STORM_FORCE = "https://thelogocompany.net/affiliate-area"
    REDITUS = "getreditus.com"
    CRAMLY_LEADDYNO = "cramly.leaddyno.com"
    TRADELLE_LEADDYNO = "tradelle.leaddyno.com"
    AFFILIATE_HIDE_MY_IP = "affiliate.hide-my-ip.com"
    AFFILIATE_SIMPLYBOOK = "affiliate.simplybook.me"
    AFFILIATE_VIPRE = "affiliate.vipre.com"
    NEURON_WRITER = "app.neuronwriter.com"
    AFFILIATE_WITHBLAZE = "affiliates.withblaze.app"
    AFFILIATE_FLOCKSOCIAL = "affiliates.flocksocial.com"
    AFFILIATLYCOM = "affiliatly.com"
    POSTAFFILIATEPRO = "https://aejuice.postaffiliatepro.com/"
    DESCRIBELY = "https://partners.describely.ai/affiliates/login.php"

    def __str__(self):
        return self.name

    @property
    def loginAPI(self):
        if self in (UrlCrawler.Goaffpro, UrlCrawler.Meross_Goaffpro):
            return "https://api2.goaffpro.com/partner/login"
        if self is UrlCrawler.Shoutout:
            return "https://www.shoutout.global/checklogin"
        if self is UrlCrawler.Uppromote:
            return "https://af.uppromote.com/solar-power-store-canada/login_aff"
        if self is UrlCrawler.Linkmink:
            return "https://app.linkmink.com/api/login"
        if self is UrlCrawler.CELLXPERT:
            return "https://fiverraffiliates.com/loginaffiliate/"
        if self is UrlCrawler.BRAIN_STORM_FORCE:
            return "https://thelogocompany.net/affiliate-area/"
        if self is UrlCrawler.REDITUS:
            return "https://api.getreditus.com/auth/sign_in"
        if self is UrlCrawler.CRAMLY_LEADDYNO:
            return "https://cramly.leaddyno.com/sso"
        if self is UrlCrawler.TRADELLE_LEADDYNO:
            return "https://tradelle.leaddyno.com/sso"
        if self is UrlCrawler.AFFILIATE_HIDE_MY_IP:
            return "https://affiliate.hide-my-ip.com/login.php"
        if self is UrlCrawler.AFFILIATE_SIMPLYBOOK:
            return "https://affiliate.simplybook.me/login.php"
        if self is UrlCrawler.AFFILIATE_VIPRE:
            return "https://affiliate.vipre.com/"
        if self is UrlCrawler.NEURON_WRITER:
            return "https://app.neuronwriter.com/ucp/login"
        if self is UrlCrawler.AFFILIATE_WITHBLAZE:
            return "https://affiliates.withblaze.app/login"
        if self is UrlCrawler.AFFILIATE_FLOCKSOCIAL:
            return "https://affiliates.flocksocial.com/login"

    @property
    def loginCheckAPI(self):
        if self is UrlCrawler.AFFILIATE_WITHBLAZE:
            return "https://affiliates.withblaze.app/login_check"
        if self is UrlCrawler.AFFILIATE_FLOCKSOCIAL:
            return "https://affiliates.flocksocial.com/login_check"

    @property
    def dataAPI(self):
        if self in (UrlCrawler.Goaffpro, UrlCrawler.Meross_Goaffpro):
            return "https://api2.goaffpro.com/partner/sales/summary/1672506000000/1701502813931"
        if self is UrlCrawler.Shoutout:
            return "https://www.shoutout.global/userdashboard"
        if self is UrlCrawler.Uppromote:
            return "https://af.uppromote.com/solar-power-store-canada/dashboard"
        if self is UrlCrawler.Linkmink:
            return "https://app.linkmink.com/api/login"
        if self is UrlCrawler.CELLXPERT:
            return "https://affiliateapi.cellxpert.com/?command=DashboardOverview"
        if self is UrlCrawler.BRAIN_STORM_FORCE:
            return "https://thelogocompany.net/affiliate-area/"
        if self is UrlCrawler.REDITUS:
            return "https://api.getreditus.com/api/affiliate/dashboard/cards"
        if self is UrlCrawler.CRAMLY_LEADDYNO:
            return "https://cramly.leaddyno.com/affiliate"
        if self is UrlCrawler.TRADELLE_LEADDYNO:
            return "https://tradelle.leaddyno.com/affiliate"
        if self is UrlCrawler.NEURON_WRITER:
            return "https://app.neuronwriter.com/ucp/affiliate"

    @property
    def tokenAPI(self):
        if self is UrlCrawler.Linkmink:
            return "https://app.linkmink.com/api/v0.1.0"
        if self is UrlCrawler.CELLXPERT:
            return "https://fiverraffiliates.com/affiliatev2/"
        if self is UrlCrawler.AFFILIATE_VIPRE:
            return "https://affiliate.vipre.com/publisher/"
        if self is UrlCrawler.AFFILIATE_WITHBLAZE:
            return "https://affiliates.withblaze.app/_form_params/"
        if self is UrlCrawler.AFFILIATE_FLOCKSOCIAL:
            return "https://affiliates.flocksocial.com/_form_params/"


class DataCrawler:
    def __init__(self, data):
        self.data = data

    # step 1: solve captcha
    async def solve_captcha(self, WEBSITE_URL, WEBSITE_KEY):
        API_KEY = "b238f538e55b7deb0da93267f61d8763"
        client_options = ClientOptions(api_key=API_KEY)
        cap_monster_client = CapMonsterClient(options=client_options)
        recaptcha2request = RecaptchaV2ProxylessRequest(
            websiteUrl=WEBSITE_URL, websiteKey=WEBSITE_KEY
        )
        return await cap_monster_client.solve_captcha(recaptcha2request)

    # step 2: Login and get authentication
    def extract_cookies_from_header(self, set_cookie_header):  # Uppromote
        cookies = re.findall(r"Set-Cookie: (.*?);", set_cookie_header)
        cookies_string = "; ".join(cookies)
        return cookies_string

    async def getTokenFromLinkMink(self, response):  # Linkmink
        data = await response.json()
        cgid = data["groups"][0]["id"]
        userID = data["userID"]
        authToken = None
        async with aiohttp.ClientSession() as session:
            headers = {"Cookie": response.headers.get("Set-Cookie")}
            async with session.get(
                f"{str(UrlCrawler.Linkmink.loginAPI)[:str(UrlCrawler.Linkmink.loginAPI).rfind('/')]}/users/{userID}/auth-token",
                headers=headers,
            ) as responseAuth:
                if response.status == 200:
                    authToken = (await responseAuth.json())["token"] if response else ""
                else:
                    print(f"Error LinkMink: {response.status}")
        if authToken:
            async with aiohttp.ClientSession() as session:
                headers = {"Authorization": f"Bearer {authToken}"}
                async with session.get(
                    f"{UrlCrawler.Linkmink.tokenAPI}/token?cgid={cgid}", headers=headers
                ) as responseAuth:
                    if response.status == 200:
                        token = (
                            (await responseAuth.json())["data"]["jwt"]
                            if response
                            else ""
                        )
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

    async def getAuthFromResponse(self, url, response, payload):
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
                id = self.extract_info_from_html(
                    r"/userdashboard\?id=([a-zA-Z0-9]+)", html_content
                )
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
                        headers = {"Cookie": cookies}
                        async with aiohttp.ClientSession() as session:
                            async with session.get(
                                str(UrlCrawler.CELLXPERT.tokenAPI), headers=headers
                            ) as responseAuth:
                                if responseAuth.status == 200:
                                    page_content = await responseAuth.text()
                                    affiliateApiToken = self.extract_info_from_html(
                                        r'localStorage\.setItem\("affiliateApiToken",\s*\'([^\']+)\'\)',
                                        page_content,
                                    )
                                    if affiliateApiToken:
                                        return affiliateApiToken
                                    else:
                                        cookies += "; rbzid=" + str(
                                            self.extract_info_from_html(
                                                r'seed\s*[:=]\s*["\']([^"\']+)["\']',
                                                page_content,
                                            )
                                        )
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
            if response.status == 302 or response.status == 200:
                if response:
                    return "; ".join(
                        f"{k}={v.value}" for k, v in response.cookies.items()
                    )
                else:
                    print("Không tìm thấy cookies.")
            else:
                print(
                    f"Error BRAIN_STORM_FORCE {response.status}: {await response.text()}"
                )
                response.raise_for_status()
            return None
        elif url == UrlCrawler.REDITUS.loginAPI:
            if response.status == 200:
                return response.headers["Authorization"]
            else:
                print("REDITUS: Không tìm thấy cookies!")
        elif (UrlCrawler.CRAMLY_LEADDYNO.value in url or UrlCrawler.TRADELLE_LEADDYNO.value in url):
            return response.headers["Set-Cookie"]
        elif url == UrlCrawler.AFFILIATE_VIPRE.tokenAPI:
            content = await response.read()
            html_content = content.decode("utf-8")
            try:
                session_token = self.extract_info_from_html(r'"session_token":"(.*?)"', html_content)
                if session_token:
                    return session_token
                else:
                    print(f"AFFILIATE_VIPRE: {payload} Session Token not found. Maybe This account has been locked.")
            except:
                print(f"AFFILIATE_VIPRE: {payload} Error extracting Session Token")
                return
        elif url == UrlCrawler.NEURON_WRITER.loginAPI:
            responseCookies = response.cookies.get("contai_session_id")
            sessionId = responseCookies.key + "=" + responseCookies.value
            return sessionId

    async def LoginAndGetAuthAsync(self, url, payload, headers, **kwargs):
        if (UrlCrawler.AFFILIATE_FLOCKSOCIAL.value in url or UrlCrawler.AFFILIATE_WITHBLAZE.value in url):
            async def get_csrf_token_from_html(html_content):
                soup = BeautifulSoup(html_content, "html.parser")
                script_tag = soup.find(
                    "script", string=lambda s: "window.configObj" in s
                )
                if script_tag:
                    script_content = script_tag.string
                    csrf_token_start = (
                        script_content.find("csrf_token:") + len("csrf_token:")
                        if script_content
                        else None
                    )
                    csrf_token_end = (
                        script_content.find(",", csrf_token_start)
                        if script_content
                        else None
                    )
                    csrf_token = (
                        script_content[csrf_token_start:csrf_token_end]
                        .strip()
                        .strip("'\"")
                        if script_content
                        else None
                    )
                    return csrf_token
                else:
                    print(
                        "Script not found or does not contain the necessary information."
                    )

            loginAPI = (
                UrlCrawler.AFFILIATE_FLOCKSOCIAL.loginAPI
                if UrlCrawler.AFFILIATE_FLOCKSOCIAL.value in url
                else UrlCrawler.AFFILIATE_WITHBLAZE.loginAPI
            )
            loginCheckAPI = (
                UrlCrawler.AFFILIATE_FLOCKSOCIAL.loginCheckAPI
                if UrlCrawler.AFFILIATE_FLOCKSOCIAL.value in url
                else UrlCrawler.AFFILIATE_WITHBLAZE.loginCheckAPI
            )
            tokenAPI = (
                UrlCrawler.AFFILIATE_FLOCKSOCIAL.tokenAPI
                if UrlCrawler.AFFILIATE_FLOCKSOCIAL.value in url
                else UrlCrawler.AFFILIATE_WITHBLAZE.tokenAPI
            )
            async with aiohttp.ClientSession() as session:
                r_ssid, r_csrf_token = None, None
                async with session.get(str(loginAPI), headers={}) as res:
                    if res.status == 200:
                        ssid = res.cookies.get("TAPSESSID")
                        headers = {"Cookie": f"TAPSESSID={ssid}"}
                        async with session.get(str(tokenAPI), headers={}) as res_form:
                            if res.status == 200:
                                data_res = await res_form.json()
                                token = data_res["token"]
                                isCaptcha = data_res["needs_captcha"]
                                payload = {
                                    "_csrf_token": token,
                                    "_username": kwargs.get("email"),
                                    "_password": kwargs.get("password"),
                                }
                                if isCaptcha:
                                    websiteKey = (
                                        "6LdHHAcUAAAAACOdiyUe67H3Ym6s1kKeetuiuFjd"
                                    )
                                    payload[
                                        "g-recaptcha-response"
                                    ] = self.solve_captcha(url, websiteKey)
                                async with session.post(
                                    str(loginCheckAPI), headers=headers, data=payload
                                ) as res_login:
                                    isLoginSuccess = await res_login.text()
                                    if "Dashboard | " in isLoginSuccess:
                                        r_csrf_token = await get_csrf_token_from_html(
                                            await res_login.text()
                                        )
                                        r_ssid = (
                                            session.cookie_jar.filter_cookies(url)
                                            .get("TAPSESSID")
                                            .value
                                        )
                    return r_ssid, r_csrf_token
        else:
            async with aiohttp.ClientSession() as session:
                async with session.post(
                    url, data=payload, headers=headers, allow_redirects=False
                ) as response:
                    return await self.getAuthFromResponse(url, response, payload)

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
                "Origin": urljoin(url, "/"),
                "Authorization": f'Bearer {kwargs.get("token", "")}',
            }
            async with aiohttp.ClientSession() as session:
                async with session.get(crawlUrl, headers=headers) as response:
                    data = await response.json()
                    return (
                        {str(UrlCrawler.Goaffpro): data}
                        if url in (UrlCrawler.Goaffpro.value)
                        else {str(UrlCrawler.Meross_Goaffpro): data}
                    )
        elif UrlCrawler.Shoutout.value in url:
            async with aiohttp.ClientSession() as session:
                async with session.get(
                    f"{UrlCrawler.Shoutout.dataAPI}?id={kwargs.get('id', '')}"
                ) as response:
                    if response.status == 200:
                        html_content = await response.text()
                        soup = BeautifulSoup(html_content, "html.parser")

                        total_revenue_element = soup.find(id="totalRevenueTxt")
                        return {
                            "Shoutout": {
                                "salesCommissionTxt": soup.select(
                                    ".card .card-body h1.card-title"
                                )[0].get_text(strip=True),
                                "leadTxt": soup.select(
                                    ".card .card-body h1.card-title"
                                )[1].get_text(strip=True),
                                "totalRevenueTxt": total_revenue_element.get_text(
                                    strip=True
                                )
                                if total_revenue_element is not None
                                else None,
                                "totalCommissionTxt": soup.select(
                                    ".card .card-body .col-12 h2"
                                )[1].get_text(strip=True),
                                "pendingCommissionTxt": soup.select(
                                    ".card .card-body .col-12 h2"
                                )[2].get_text(strip=True),
                            }
                        }
                    else:
                        print(f"Error: {response.status}")
                        return None
        elif url == UrlCrawler.Uppromote.value:
            headers = {"Cookie": kwargs.get("cookie", "")}
            async with aiohttp.ClientSession() as session:
                async with session.get(
                    str(UrlCrawler.Uppromote.dataAPI), headers=headers
                ) as response:
                    if response.status == 200:
                        html_content = await response.text()
                        soup = BeautifulSoup(html_content, "html.parser")

                        selected_elements = soup.select(
                            "#commission .panel-body__pending, #commission .panel-body__approved, #commission .panel-body__paid"
                        )
                        return {
                            "Uppromote": {
                                label_element.text.strip(): element.text.strip()
                                for element in selected_elements
                                if (label_element := element.find_next(class_="my-0"))
                                is not None
                            }
                        }
                    else:
                        print(f"Error: {response.status}")
                        return None
        elif url == UrlCrawler.Linkmink.value:
            traffic = 0
            conversions = 0
            commissions = 0

            headers = {
                "Authorization": f'Bearer {kwargs.get("authToken", "")}',
                "Cookie": kwargs.get("cookie", "")
                + f';lm_auth={kwargs.get("token", "")}',
            }
            first_day, last_day = self.get_first_and_last_day(
                datetime.now().year, datetime.now().month
            )
            async with aiohttp.ClientSession() as session:
                async with session.get(
                    f"{UrlCrawler.Linkmink.tokenAPI}/clicks/metrics?livemode=true&min_date={self.convert_to_unix_timestamp(first_day)}&max_date={self.convert_to_unix_timestamp(last_day)}&timezone=Asia%2FBangkok",
                    headers=headers,
                ) as response:
                    if response.status == 200:
                        result = await response.json()
                        traffic = result["metrics"]
                    else:
                        print(f"Error: {response.status} -  {await response.text()}")

            async with aiohttp.ClientSession() as session:
                async with session.get(
                    f"{UrlCrawler.Linkmink.tokenAPI}/conversions/metrics?livemode=true&min_date={self.convert_to_unix_timestamp(first_day)}&max_date={self.convert_to_unix_timestamp(last_day)}&withCredentials=true&timezone=Asia%2FBangkok",
                    headers=headers,
                ) as response:
                    if response.status == 200:
                        result = await response.json()
                        conversions = result["metrics"]
                    else:
                        print(f"Error: {response.status} - {await response.text()}")

            async with aiohttp.ClientSession() as session:
                async with session.get(
                    f"{UrlCrawler.Linkmink.tokenAPI}/commissions/metrics?livemode=true&min_date={self.convert_to_unix_timestamp(first_day)}&max_date={self.convert_to_unix_timestamp(last_day)}&timezone=Asia%2FBangkok",
                    headers=headers,
                ) as response:
                    if response.status == 200:
                        result = await response.json()
                        commissions = result["metrics"]
                    else:
                        print(f"Error: {response.status} -  {await response.text()}")
            return {
                "Linkmink": {
                    "traffic": traffic,
                    "conversions": conversions,
                    "commissions": commissions,
                }
            }
        elif url == UrlCrawler.CELLXPERT.value:
            headers = {
                "affiliate_url": "Fiverr",
                "Authorization": f"Bearer {kwargs.get('token', '')}",
            }
            first_day, last_day = self.get_first_and_last_day(
                datetime.now().year, datetime.now().month
            )
            async with aiohttp.ClientSession() as session:
                async with session.get(
                    f"{UrlCrawler.CELLXPERT.dataAPI}&enddate={quote(last_day.strftime('%m/%d/%Y'))}&startdate={quote(first_day.strftime('%m/%d/%Y'))}&uniqueId=793046888",
                    headers=headers,
                ) as response:
                    if response.status == 200:
                        result = await response.json()
                        return {"CELLXPERT": result}
                    else:
                        print(
                            f"Error CELLXPERT {response.status}: {await response.text()}"
                        )
                        return None
        elif url == UrlCrawler.BRAIN_STORM_FORCE.value:
            headers = {"Cookie": kwargs.get("cookie", "")}
            first_day, last_day = self.get_first_and_last_day(
                datetime.now().year, datetime.now().month
            )
            async with aiohttp.ClientSession() as session:
                async with session.get(
                    str(UrlCrawler.BRAIN_STORM_FORCE.dataAPI), headers=headers
                ) as response:
                    if response.status == 200:
                        html_content = await response.text()
                        soup = BeautifulSoup(html_content, "html.parser")
                        keys = soup.select(
                            ".text-sm.leading-5.font-medium.text-gray-500.truncate"
                        )
                        values = soup.select(".items-baseline div")
                        return {
                            "BRAIN_STORM_FORCE": {
                                key.text.strip(): value.text.strip()
                                for key, value in zip(keys, values)
                            }
                        }
                    else:
                        print(
                            f"Error BRAIN_STORM_FORCE {response.status}: {await response.text()}"
                        )
                        return None
        elif UrlCrawler.REDITUS.value in url:
            headers = {
                "Authorization": f"{kwargs.get('token', '')}",
                "Content-Type": "application/json",
            }
            async with aiohttp.ClientSession() as session:
                async with session.get(
                    str(UrlCrawler.REDITUS.dataAPI), headers=headers
                ) as response:
                    return await response.json()
        elif (UrlCrawler.CRAMLY_LEADDYNO.value in url or UrlCrawler.TRADELLE_LEADDYNO.value in url):
            getInfoHeaders = {
                ":method": "GET",
                ":authority": "tradelle.leaddyno.com",
                ":scheme": "https",
                ":path": "/affiliate",
                # "sec-ch-ua": "Not_A Brand";v="8", "Chromium";v="120", "Microsoft Edge";v="120",
                "sec-ch-ua-mobile": "?0",
                "sec-ch-ua-platform": "Windows",
                "upgrade-insecure-requests": "1",
                "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36 Edg/120.0.0.0",
                "accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.7",
                "sec-fetch-site": "same-origin",
                "sec-fetch-mode": "navigate",
                "sec-fetch-user": "?1",
                "sec-fetch-dest": "document",
                "referer": "https://tradelle.leaddyno.com/",
                "accept-encoding": "gzip, deflate, br",
                "accept-language": "en-US,en;q=0.9",
                "cookie": kwargs.get("token", ""),
                "if-none-match": "W/'2fc70b5ebd7a45aad667e0be52dbb996'",
            }
            dataRequestUrl = ""
            if UrlCrawler.CRAMLY_LEADDYNO.value in url:
                dataRequestUrl = UrlCrawler.CRAMLY_LEADDYNO.dataAPI
            if UrlCrawler.TRADELLE_LEADDYNO.value in url:
                dataRequestUrl = UrlCrawler.TRADELLE_LEADDYNO.dataAPI
            async with aiohttp.ClientSession() as session:
                async with session.get(
                    str(dataRequestUrl),
                    headers={**getInfoHeaders},
                    allow_redirects=False,
                ) as response:
                    content = (
                        await response.read()
                    )  # Read the response content as bytes
                    # Decode the bytes to a string
                    pageSource = content.decode("utf-8")
                    soup = BeautifulSoup(pageSource, "html.parser")
                    results = soup.select(".aff-progress-digit>b")
                    resultsContent = [int(element.text) for element in results]
                    result_dict = {}
                    if len(resultsContent) > 0:
                        result_dict = {
                            "Visited": resultsContent[0],
                            "Signed up": resultsContent[1],
                            "Purchases": resultsContent[2],
                        }
                    return result_dict
        elif (UrlCrawler.AFFILIATE_HIDE_MY_IP.value in url or UrlCrawler.AFFILIATE_SIMPLYBOOK.value in url):
            loginAPI = (
                UrlCrawler.AFFILIATE_HIDE_MY_IP.loginAPI
                if UrlCrawler.AFFILIATE_HIDE_MY_IP.value in url
                else UrlCrawler.AFFILIATE_SIMPLYBOOK.loginAPI
            )
            headers = {"Content-Type": "application/x-www-form-urlencoded"}
            payload = f"csrf_token=&userid={kwargs.get('email')}&password={kwargs.get('password')}&token_affiliate_login=2eed4d63883d9ed92399"
            async with aiohttp.ClientSession() as session:
                async with session.post(
                    str(loginAPI), data=payload, headers=headers
                ) as response:
                    content = (
                        await response.read()
                    )  # Read the response content as bytes
                    # Decode the bytes to a string
                    pageSource = content.decode("utf-8")
                    soup = BeautifulSoup(pageSource, "html.parser")
                    results = soup.select(".heading")
                    resultsContent = [element.text.strip() for element in results]
                    lastElement = resultsContent[len(resultsContent) - 1]
                    twoLastElement = lastElement.replace(" ", "").split("\n\n")
                    resultsContent.pop()
                    resultsContent = resultsContent + twoLastElement
                    if len(resultsContent) > 0:
                        result_dict = {
                            "Total Transactions": resultsContent[0],
                            "Current Earnings": resultsContent[1],
                            "Total Earned To Date": resultsContent[2],
                            "Unique Visitors": resultsContent[3],
                            "Sales Ratio": resultsContent[4],
                        }
                        return result_dict
        elif UrlCrawler.AFFILIATE_VIPRE.value in url:
            dataPayload = {
                "fields[]": [
                    "Stat.impressions",
                    "Stat.clicks",
                    "Stat.conversions",
                    "Stat.payout",
                ],
                "Method": "getStats",
                "NetworkId": "vipre",
                "SessionToken": kwargs.get("token"),
            }
            async with aiohttp.ClientSession() as session:
                async with session.post(
                    "https://api-p03.hasoffers.com/v3/Affiliate_Report.json",
                    data=dataPayload,
                ) as response:
                    content = await response.json()
                    if content:
                        return content["response"]["data"]["data"]
                    else:
                        print("Has offer: No 'response' attribute in the JSON content.")
        elif url == UrlCrawler.NEURON_WRITER.dataAPI:
            headers = {"Cookie": kwargs.get("sessionId")}
            async with aiohttp.ClientSession() as session:
                async with session.get(
                    str(UrlCrawler.NEURON_WRITER.dataAPI), headers=headers
                ) as response:
                    content = await response.read()
                    pageSource = content.decode("utf-8")
                    soup = BeautifulSoup(pageSource, "html.parser")
                    data = []
                    for row in soup.select(
                        'table[data-export_fname="aff_daily_stats"] tbody tr'
                    ):
                        date = row.select("td")[0].text.strip()
                        clicks = row.select("td")[1].text.strip()
                        unique_ips = row.select("td")[2].text.strip()
                        entry = {
                            "date": date,
                            "clicks": clicks,
                            "unique IPs": unique_ips,
                        }
                        data.append(entry)
                return data
        elif (UrlCrawler.AFFILIATE_FLOCKSOCIAL.value in url or UrlCrawler.AFFILIATE_WITHBLAZE.value in url):
            ssid = kwargs.get("ssid")
            csrf_token = kwargs.get("csrf_token")
            current_date = datetime.now()
            date_30_days_ago = current_date - timedelta(days=30)
            date_format = "%Y-%m-%d"
            # Convert to formatted strings
            current_date_str = current_date.strftime(date_format)
            date_30_days_ago_str = date_30_days_ago.strftime(date_format)
            url = f"{url}/api-stateful/pi/reports-depr/date/?date_from={date_30_days_ago_str}&date_to={current_date_str}&sort_by=title&sort_direction=DESC&page=1"
            payload = None
            headers = {}
            headers["Cookie"] = f"TAPSESSID={ssid}"
            headers["X-Csrf-Token"] = csrf_token
            async with aiohttp.ClientSession() as session:
                async with session.get(url, headers=headers, data=payload) as response0:
                    if response0.status == 200:
                        dict_data = await response0.json()
                        return dict_data["results"]
                        # for item in dict_data["results"]:
                        #     print(item)
                    else:
                        print("Error fetch data", response0.text)
        elif UrlCrawler.AFFILIATLYCOM.value in url:
            async with aiohttp.ClientSession() as session:
                _url = f"{url}/af-1040475/affiliate.panel"
                async with session.get(_url, headers={}) as response:
                    ssid = response.cookies.get("PHPSESSID")
                    soup = BeautifulSoup(await response.text(), "html.parser")
                    login_hsf_input = soup.find("input", {"name": "login_hsf"})
                    login_hsf_value = (
                        login_hsf_input["value"] if login_hsf_input else None
                    )
                    login_hsf_time_input = soup.find(
                        "input", {"name": "login_hsf_time"}
                    )
                    login_hsf_time_value = (
                        login_hsf_time_input["value"] if login_hsf_time_input else None
                    )

                _url = f"{url}/af-1040475/affiliate.panel"
                payload = {
                    "email": kwargs.get("email"),
                    "password": kwargs.get("password"),
                    "captcha": "",
                    "login_hsf": login_hsf_value,
                    "login_hsf_time": login_hsf_time_value,
                    "login": "",
                }

                async with session.post(_url, headers={}, data=payload) as response:
                    _affiliatly_logged = (
                        session.cookie_jar.filter_cookies(_url)
                        .get("_affiliatly_logged")
                        .value
                    )
                    if _affiliatly_logged is not None:
                        headers = {}
                        headers[
                            "Cookie"
                        ] = f"PHPSESSID={ssid}; _affiliatly_logged={_affiliatly_logged}"
                        _url = f"{url}/af-1040475/affiliate.panel"
                        async with session.get(_url, headers=headers) as response:
                            html_content = await response.text()
                            soup = BeautifulSoup(html_content, "html.parser")
                            unpaid_div = soup.find("div", class_="pull-left half_row")
                            unpaid_value = unpaid_div.strong.text
                            # table = soup.find('table', class_='stats_n_orders')
                            total_row = soup.find("td", string="Total:").parent
                            visitors_total = (
                                total_row.find_all("td")[1].text if total_row else None
                            )
                            orders_total = (
                                total_row.find_all("td")[2].text if total_row else None
                            )
                            earnings_total = (
                                total_row.find_all("td")[4].text if total_row else None
                            )
                            data_crawl = {
                                "Unpaid Earnings": unpaid_value,
                                "Total Visitors": visitors_total,
                                "Total Orders": orders_total,
                                "Total Your Earnings": earnings_total,
                            }
                            return data_crawl
                    else:
                        return f"Error with login website , {url}"

    # Crawl data func
    async def crawl_data(self, args):
        if len(args) <= 0:
            print("Insufficient number of arguments.")
            return None
        url, email, password = args
        if url in (UrlCrawler.Goaffpro.value, UrlCrawler.Meross_Goaffpro.value):
            WEBSITE_KEY = "6Lf_jsQUAAAAAOLW40PpDXgZQDIjjnGldAE1fhYr"
            res = await self.solve_captcha(url, WEBSITE_KEY)
            payload = {
                "email": email,
                "password": password,
                "partner_portal_subdomain": "allpowers.goaffpro.com",
                "recaptcha_response": res["gRecaptchaResponse"],
            }
            headers = {"Origin": urljoin(url, "/")}

            token = await self.LoginAndGetAuthAsync(
                UrlCrawler.Meross_Goaffpro.loginAPI, payload, headers
            )
            if token:
                first_day, last_day = self.get_first_and_last_day(
                    datetime.now().year, datetime.now().month
                )
                data = await self.fetch_data(
                    url, startDate=first_day, endDate=last_day, token=token
                )
                return data
            else:
                print("Failed to obtain token.")
                return None
        elif UrlCrawler.Shoutout.value in url:
            WEBSITE_KEY = "6LfvfrEUAAAAAPg5Dt1q3UsmCwD_Z5oELX4s95eB"
            encryptedID = parse_qs(urlparse(url).query)
            res = await self.solve_captcha(url, WEBSITE_KEY)
            payload = {
                "email": email,
                "password": password,
                "g-recaptcha-response": res["gRecaptchaResponse"],
                "encryptedID": encryptedID["id"][0],
            }
            headers = {"Origin": urljoin(url, "/")}
            id = await self.LoginAndGetAuthAsync(
                UrlCrawler.Shoutout.loginAPI, payload, headers
            )
            if id:
                data = await self.fetch_data(url, id=id)
                return data
            else:
                print("Failed to obtain ID.")
                return None
        elif url == UrlCrawler.Uppromote.value:
            WEBSITE_KEY = "6LcfFqkaAAAAAODkHHT2DLE7UBeSbf7kVCdBkTQE"
            res = await self.solve_captcha(url, WEBSITE_KEY)
            payload = {
                "_token": "5xhC3w0BB9Cezh7fhtZJg5YaHJvyInW5AC4qy8Mi",
                "shop_id": "80375",
                "email": email,
                "password": password,
                "g-recaptcha-response": res["gRecaptchaResponse"],
            }
            headers = {}

            cookie = await self.LoginAndGetAuthAsync(
                UrlCrawler.Uppromote.loginAPI, payload, headers
            )

            return await self.fetch_data(url, cookie=cookie)
        elif url == UrlCrawler.Linkmink.value:
            payload = {"username": email, "password": password}
            headers = {}

            result = await self.LoginAndGetAuthAsync(
                UrlCrawler.Linkmink.loginAPI, payload, headers
            )
            if result and len(result) == 3:
                token, authToken, cookie = result
                return await self.fetch_data(
                    url, token=token, authToken=authToken, cookie=cookie
                )
        elif url == UrlCrawler.CELLXPERT.value:
            payload = {
                "action": "affiliates_login",
                "token": "",
                "errorurl": "https://affiliates.fiverr.com/",
                "command": "logon",
                "user": email,
                "password": password,
                "rememberme": "on",
            }

            headers = {}

            token = await self.LoginAndGetAuthAsync(
                UrlCrawler.CELLXPERT.loginAPI, payload, headers
            )
            if token:
                return await self.fetch_data(url, token=token)
        elif url == UrlCrawler.BRAIN_STORM_FORCE.value:
            affwp_login_nonce = ""
            async with aiohttp.ClientSession() as session:
                async with session.get(str(UrlCrawler.BRAIN_STORM_FORCE.dataAPI)) as response:
                    html_content = await response.text()                    
                    soup = BeautifulSoup(html_content, 'html.parser')
                    affwp_login_nonce_input = soup.select_one('input[name="affwp_login_nonce"]')
                    if not affwp_login_nonce_input: return
                    affwp_login_nonce = affwp_login_nonce_input['value']

            payload = {
                "affwp_user_login": email,
                "affwp_user_pass": password,
                "affwp_user_remember": "1",
                "affwp_redirect": "",
                "affwp_login_nonce": affwp_login_nonce,
                "affwp_action": "user_login",
            }
            headers = {}
            cookie = await self.LoginAndGetAuthAsync(
                UrlCrawler.BRAIN_STORM_FORCE.loginAPI, payload, headers
            )
            if cookie:
                return await self.fetch_data(url, cookie=cookie)
        elif UrlCrawler.REDITUS.value in url:
            payload = {"email": email, "password": password}
            headers = {}
            token = await self.LoginAndGetAuthAsync(
                UrlCrawler.REDITUS.loginAPI, payload, headers
            )
            if token:
                return await self.fetch_data(url, token=token)
        elif (UrlCrawler.CRAMLY_LEADDYNO.value in url or UrlCrawler.TRADELLE_LEADDYNO.value in url):
            payload = {
                "ic-request": "true",
                "password": password,
                "email": email,
                "ic-id": 1,
                "ic-current-url": "/",
                "_method": "PUT",
            }
            headers = {}
            loginAPI = (
                UrlCrawler.CRAMLY_LEADDYNO.loginAPI if UrlCrawler.CRAMLY_LEADDYNO.value in url else UrlCrawler.TRADELLE_LEADDYNO.loginAPI
            )
            token = await self.LoginAndGetAuthAsync(loginAPI, payload, headers)
            if token:
                return await self.fetch_data(url, token=token)
        elif (UrlCrawler.AFFILIATE_HIDE_MY_IP.value in url or UrlCrawler.AFFILIATE_SIMPLYBOOK.value in url):
            return await self.fetch_data(url, email=email, password=password)
        elif UrlCrawler.AFFILIATE_VIPRE.value in url:
            sessionIdPayload = {
                "data[User][email]": email,
                "data[User][password]": password,
            }
            sessionIdHeaders = {
                "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/77.0.3865.90 Safari/537.36",
                "accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.7",
                "accept-encoding": "gzip, deflate, br",
                "connection": "keep-alive",
                "cookie": "EUcomp=1",
                "content-type": "application/x-www-form-urlencoded",
            }
            async with aiohttp.ClientSession() as session:
                async with session.post(
                    str(UrlCrawler.AFFILIATE_VIPRE.loginAPI),
                    data=sessionIdPayload,
                    headers=sessionIdHeaders,
                    allow_redirects=False,
                ) as response:
                    responseCookies = response.cookies.get("PHPSESSID")
                    sessionId = (
                        responseCookies.key + "=" + responseCookies.value
                        if responseCookies
                        else None
                    )
            tokenHeaders = {"Cookie": sessionId}
            token = await self.LoginAndGetAuthAsync(
                UrlCrawler.AFFILIATE_VIPRE.tokenAPI, sessionIdPayload, tokenHeaders
            )
            if token:
                return {
                    "AFFILIATE_VIPRE": await self.fetch_data(url, token=token)
				}
        elif UrlCrawler.NEURON_WRITER.value in url:
            payload = {"email": email, "password": password, "redirect_url": "/"}
            sessionId = await self.LoginAndGetAuthAsync(
                UrlCrawler.NEURON_WRITER.loginAPI, payload, {}
            )
            return await self.fetch_data(
                UrlCrawler.NEURON_WRITER.dataAPI, sessionId=sessionId
            )
        elif (UrlCrawler.AFFILIATE_FLOCKSOCIAL.value in url or UrlCrawler.AFFILIATE_WITHBLAZE.value in url):
            ssid, csrf_token = await self.LoginAndGetAuthAsync(
                url, None, None, email=email, password=password
            )
            if ssid:
                return await self.fetch_data(url, ssid=ssid, csrf_token=csrf_token)
            else:
                print("Lấy token không thành công: {}".format(url))
        elif UrlCrawler.AFFILIATLYCOM.value in url:
            return await self.fetch_data(url, email=email, password=password)
        elif (UrlCrawler.DESCRIBELY.value in url or UrlCrawler.POSTAFFILIATEPRO.value in url):
            crawler = DescribelyAndPostaffiliateproCrawler(*args)
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
    # ('https://api.getreditus.com/auth/sign_in', 'alishacooper125we@gmail.com', 'sB"K3??9^8;n'),
    # ('https://api.getreditus.com/auth/sign_in', 'staakerole@gmail.com', 'QqHzAXjVR8#uBBN'),
    # ('https://cramly.leaddyno.com/sso', 'teamasmads@gmail.com', 'yqZWRKe6hrYmS4u'), #This affiliate program has been deactivated by the owner
    # ('https://tradelle.leaddyno.com/sso', 'teamasmads@gmail.com', '2fijD4FNfM4Z@pj'),
    # ('https://affiliate.hide-my-ip.com/login.php', 'beckyanderson23g', 'CqA5v9BvI6J0'),
    # ('https://affiliate.simplybook.me/login.php', 'emilymurphy965df', 'L4AYLVa97S'),
    # ('https://affiliate.vipre.com/', 'evenelson380df@gmail.com', 'A61yIU8g4!f)'),
    # ('https://affiliate.vipre.com/', 'alishacooper125we@gmail.com', 'J9figOCIfbMICXB'),
    ('https://affiliate.vipre.com/', 'asmlongle@gmail.com', 'tj5kLv2dNmZgZ!f'), 
    # ('https://app.neuronwriter.com/ucp/', 'eleanorlewis676rsdf@gmail.com', 'C9xvPC$SCcU;6~V'),
    # ('https://www.affiliatly.com/af-1031650/affiliate.panel', 'teamasmads@gmail.com', '2N*G5k$7ux5j2!F'),
    # ('https://www.affiliatly.com/af-1040475/affiliate.panel', 'beckyanderson23g@gmail.com', '9qWWo95F31Nq@'),
    # ('https://aejuice.postaffiliatepro.com/affiliates/', 'charlotteflores549sd@gmail.com', 'Utuw1ZR05b'),
    # ('https://partners.describely.ai/affiliates/login.php', 'emilymurphy965df@gmail.com', 'heqadqlTk8Z601T'),
    # ("https://affiliates.withblaze.app", "maddietaylor376cv@gmail.com", "Aceu9YO60m"),
    # ('https://affiliates.flocksocial.com', 'beckyanderson23g@gmail.com', 'hI8p63uW90a9')
]


async def main():
    crawler = DataCrawler(data)
    await crawler.crawl()

# Chạy chương trình chính
if __name__ == "__main__":
    asyncio.run(main())
