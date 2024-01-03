"""
    Custom from https://github.com/LeLyThiTun2708/ASM-Crawl
"""
import aiohttp
from bs4 import BeautifulSoup
import json
from datetime import datetime, timedelta
from capmonstercloudclient import CapMonsterClient, ClientOptions
from capmonstercloudclient.requests import RecaptchaV2ProxylessRequest

class Crawler:
    def __init__(self, url, username, password) -> None:
        self.url = url
        self.username = username
        self.password = password
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

class WithblazeAndFlocksocialCrawler(Crawler):
    def __init__(self, url, username, password) -> None:
        super().__init__(url, username, password)

    async def solve_captcha(self, input_url):
        client_options = ClientOptions(api_key='b238f538e55b7deb0da93267f61d8763')
        cap_monster_client = CapMonsterClient(options=client_options)
        recaptcha2request = RecaptchaV2ProxylessRequest(
            websiteUrl=f"{input_url}/login_check",
            websiteKey="6LdHHAcUAAAAACOdiyUe67H3Ym6s1kKeetuiuFjd"
        )
        return await cap_monster_client.solve_captcha(recaptcha2request)

    async def get_csrf_token_from_html(self, html_content):
        soup = BeautifulSoup(html_content, 'html.parser')
        script_tag = soup.find('script', string=lambda s: 'window.configObj' in s)
        if script_tag:
            script_content = script_tag.string
            csrf_token_start = script_content.find('csrf_token:') + len('csrf_token:')
            csrf_token_end = script_content.find(',', csrf_token_start)
            csrf_token = script_content[csrf_token_start:csrf_token_end].strip().strip('\'"')
            return csrf_token
        else:
            print("Script not found or does not contain the necessary information.")

    async def crawl(self):
        # Edit url
        last_string = self.url[-1]
        if last_string == "/":
            self.url = self.url[:-1]
        async with aiohttp.ClientSession() as session:
            url = f"{self.url}/login"
            ssid = ''
            async with session.get(url, headers=self.default_headers) as res:
                if res.status == 200:
                    ssid = res.cookies.get('TAPSESSID')
                else:
                    print(f"Error: {res.status} | {await res.text()}")
            # request to get token login
            headers = self.default_headers
            headers['Cookie'] = f'TAPSESSID={ssid}'
            url = f"{self.url}/_form_params/"
            token = ''
            isCaptcha = False

            async with session.get(url, headers=self.default_headers) as res_form:
                if res.status == 200:
                    data_res = await res_form.json()
                    token = data_res["token"]
                    isCaptcha = data_res["needs_captcha"]
            if isCaptcha is False:
                payload = {
                    "_csrf_token": token,
                    "_username": self.username,
                    "_password": self.password,
                }
            else:
                payload = {
                    "_csrf_token": token,
                    "_username": self.username,
                    "_password": self.password,
                    "g-recaptcha-response": await self.solve_captcha(self.url),
                }
            url = f"{self.url}/login_check"
            headers = self.default_headers
            headers['Cookie'] = f'TAPSESSID={ssid}'

            async with session.post(url, headers=headers, data=payload) as res_login:
                new_ssid = ''
                new_csrf_token = ''
                isLoginSuccess = await res_login.text()
                if "Dashboard | " in isLoginSuccess:
                    new_csrf_token = await self.get_csrf_token_from_html(await res_login.text())
                    new_ssid = session.cookie_jar.filter_cookies(url).get("TAPSESSID").value
                    # Get day now
                    current_date = datetime.now()
                    # Subtract 30 days
                    date_30_days_ago = current_date - timedelta(days=30)
                    # Format for day/month/year
                    date_format = "%Y-%m-%d"
                    # Convert to formatted strings
                    current_date_str = current_date.strftime(date_format)
                    date_30_days_ago_str = date_30_days_ago.strftime(date_format)
                    url = f"{self.url}/api-stateful/pi/reports-depr/date/?date_from={date_30_days_ago_str}&date_to={current_date_str}&sort_by=title&sort_direction=DESC&page=1"
                    payload=None
                    # print("Fetch Data")
                    headers = self.default_headers
                    headers['Cookie'] = f'TAPSESSID={new_ssid}'
                    headers['X-Csrf-Token'] = new_csrf_token
                    async with session.get(url, headers=headers, data=payload) as response0:
                        if response0.status == 200:
                            # print(response0.status)
                            dict_data = await response0.json()
                            return dict_data['results']
                            # for item in dict_data["results"]:
                            #     print(item)
                        else:
                            print("Error fetch data", response0.text)
                else:
                    return f"Error with login_check, {self.url}"
                
class DescribelyAndPostaffiliateproCrawler(Crawler):
    def __init__(self, url, username, password) -> None:
        super().__init__(url, username, password)

    async def crawl(self):
        idx = self.url.index("/affiliates")
        self.url = self.url[:idx]
        
        async def extract_cookie(cookie_string):
            idx1 = cookie_string.index("=")
            idx2 = cookie_string.index(";")

            cookie_string =  cookie_string[idx1+1:idx2]
            return cookie_string

        async with aiohttp.ClientSession() as session:
            url = f"{self.url}/affiliates/login.php"
            response0 = await session.get(url, headers=self.default_headers)
            signup_pap_sid = response0.cookies.get('signup_pap_sid')
            signup_pap_sid = str(signup_pap_sid)
            signup_pap_sid = await extract_cookie(signup_pap_sid)

            headers = self.default_headers
            headers['cookie'] = f'gpf_language=en-US; signup_pap_sid={signup_pap_sid}'

            json_data = {
                "C": "Gpf_Rpc_Server",
                "M": "run",
                "requests": [
                    {"C": "Gpf_Rpc_Server", "M": "syncTime", "offset": "54000000"},
                    {"C": "Gpf_Templates_TemplateService", "M": "getTemplate", "templateName": "window_move_panel"},
                    {"C": "Gpf_Templates_TemplateService", "M": "getTemplate", "templateName": "context_menu"},
                    {"C": "Gpf_Templates_TemplateService", "M": "getTemplate", "templateName": "window_header_refresh"},
                    {"C": "Gpf_Templates_TemplateService", "M": "getTemplate", "templateName": "item"},
                    {"C": "Gpf_Templates_TemplateService", "M": "getTemplate", "templateName": "single_content_panel"},
                    {"C": "Gpf_Templates_TemplateService", "M": "getTemplate", "templateName": "form_field_checkbox"},
                    {"C": "Gpf_Templates_TemplateService", "M": "getTemplate", "templateName": "login_annotation"}
                ],
                "S": signup_pap_sid
            }
            form_data = {"D": json.dumps(json_data)}
            url_post = f"{self.url}/scripts/server.php"
            response0 = await session.post(url_post, data=form_data, headers=headers)
            headers = self.default_headers
            headers['cookie'] = f'gpf_language=en-US; signup_pap_sid={signup_pap_sid}'

            json_data = {
                "C": "Gpf_Rpc_Server", "M": "run",
                "requests": [
                    {"C": "Gpf_Auth_Service", "M": "authenticate", 
                     "fields": [["name", "value"], ["Id", ""],
                    ["username", self.username], ["password", self.password],
                    ["twofactor_token", ""], ["rememberMe", "N"],
                    ["language", "en-US"], ["roleType", "A"]]}
                ],
                "S": signup_pap_sid
            }

            form_data = {"D": json.dumps(json_data)}
            response0 = await session.post(url_post, data=form_data, headers=headers)
            # isSuccess = await response0.json()

            affiliates_pap_sid = response0.cookies.get('affiliates_pap_sid')
            affiliates_pap_sid = str(affiliates_pap_sid)
            affiliates_pap_sid = await extract_cookie(affiliates_pap_sid)

            headers = self.default_headers
            headers['cookie'] = f'gpf_language=en-US; signup_pap_sid={signup_pap_sid}; affiliates_pap_sid={affiliates_pap_sid}'
            url = f"{self.url}/affiliates/panel.php"
            response0 = await session.get(url, headers=headers)

            # Sau đó request theo trình tự này, thay đổi headers sau khi lấy được affiliates_pap_sid
            json_data = {"C":"Gpf_Rpc_Server", "M":"run", "requests":[{"C":"Gpf_Rpc_Server", "M":"syncTime", "offset":"54000000"},{"C":"Gpf_Templates_TemplateService", "M":"getTemplate", "templateName":"main_header"},{"C":"Gpf_Templates_TemplateService", "M":"getTemplate", "templateName":"calendar"},{"C":"Gpf_Templates_TemplateService", "M":"getTemplate", "templateName":"date_preset_panel"},{"C":"Gpf_Templates_TemplateService", "M":"getTemplate", "templateName":"custom_date_panel"},{"C":"Gpf_Templates_TemplateService", "M":"getTemplate", "templateName":"date_range_filter_field"},{"C":"Pap_Affiliates_MainPanelHeader", "M":"load"},{"C":"Gpf_Templates_TemplateService", "M":"getTemplate", "templateName":"tooltip_popup"},{"C":"Gpf_Templates_TemplateService", "M":"getTemplate", "templateName":"form_field"},{"C":"Gpf_Templates_TemplateService", "M":"getTemplate", "templateName":"affiliate_manager"},{"C":"Gpf_Db_Table_FormFields", "M":"getTranslatedFields", "formId":"merchantForm", "status":"M,O,R"},{"C":"Gpf_Templates_TemplateService", "M":"getTemplate", "templateName":"data_field"},{"C":"Gpf_Templates_TemplateService", "M":"getTemplate", "templateName":"news_content"},{"C":"Gpf_Templates_TemplateService", "M":"getTemplate", "templateName":"simple_icon_object"},{"C":"Pap_Affiliates_MerchantInfo", "M":"load", "fields":[["name","value"],["Id",""]]},{"C":"Pap_Affiliates_Reports_PeriodStats", "M":"load"},{"C":"Pap_Common_NewsManager", "M":"loadUnread"}], 
            "S":affiliates_pap_sid}
            form_data = {"D": json.dumps(json_data)}
            response0 = await session.post(url_post, headers=headers, data=form_data)
            # 2
            json_data = {"C":"Gpf_Rpc_Server", "M":"run", "requests":[{"C":"Pap_Common_NewsManager", "M":"load"},{"C":"Pap_Common_Reports_StatisticsBaseNew", "M":"loadData", "filters":[["datetime","DP","L7D"],["groupBy","=","day"],["dataType1","=","commission"],["dataStatus1","=","A"],["dataPStatus1","=",""],["dataType2","=","commission"],["dataStatus2","=","A"],["dataPStatus2","=","P"],["dataType3","=","commission"],["dataStatus3","=","P"],["dataPStatus3","=",""]]}], 
                        "S":affiliates_pap_sid}
            form_data = {"D": json.dumps(json_data)}
            response0 = await session.post(url_post, headers=headers, data=form_data)
            # 3
            json_data = {"C":"Gpf_Rpc_Server", "M":"run", "requests":[{"C":"Gpf_Templates_TemplateService", "M":"getAllMissingTemplates", "templateName":"", "loadedTemplates":",loading_indicator,main,button,loading_template,breadcrumbs,icon_button,main_menu,menu_entry,menu_section,sub_menu_section,system_menu,window,window_move_panel,window_left,context_menu,window_header,window_header_refresh,window_bottom_left,window_empty_content,item,single_content_panel,home,link_button,main_header,calendar,date_preset_panel,custom_date_panel,date_range_filter_field,tooltip_popup,form_field,affiliate_manager,data_field,news_content,simple_icon_object", "templatesCount":50}], 
            "S":affiliates_pap_sid}
            form_data = {"D": json.dumps(json_data)}
            response0 = await session.post(url_post, headers=headers, data=form_data)
            # Sau đó request theo trình tự đến Report
            json_data = {"C":"Gpf_Rpc_Server", "M":"run", "requests":[{"C":"Gpf_Db_Table_Filters", "M":"getDefaultFilter", "data":[["name","value"],["filterType","trends_report"]]},{"C":"Gpf_Db_Table_Filters", "M":"get", "filterType":"trends_report"},{"C":"Gpf_DateTime_Range", "M":"loadDateRangeFromPreset", "datePreset":"L30D"},{"C":"Pap_Affiliates_Reports_TrendsReport", "M":"loadDefaultDataTypes"},{"C":"Pap_Affiliates_Reports_TrendsReport", "M":"loadDataTypes"},{"C":"Pap_Common_Campaign_CampaignForAffiliateTransactionsRichListBox", "M":"load", "clicks":"Y", "from":0, "rowsPerPage":20, "maxCachedCount":500, "id":"cachedRequest"},{"C":"Pap_Merchants_Campaign_AffChannelSearchRichListBox", "M":"load", "from":0, "rowsPerPage":20, "maxCachedCount":500, "id":"cachedRequest", "userid":""},{"C":"Pap_Common_Banner_BannerForAffiliateStatsRichListBox", "M":"load", "from":0, "rowsPerPage":20, "maxCachedCount":500, "id":"cachedRequest"},{"C":"Pap_Affiliates_Promo_DestinationUrlRichListBox", "M":"load", "from":0, "rowsPerPage":20, "maxCachedCount":500, "id":"cachedRequest"},{"C":"Pap_Affiliates_Reports_TrendsReport", "M":"loadData", "isInitRequest":"Y", "filterType":"trends_report", "filters":[["datetime","DP","L30D"],["rpc","=","Y"],["groupBy","=","day"],["dataType1","=","saleCount"],["dataType2","=","_item_none_"]]}], 
                        "S":affiliates_pap_sid}
            form_data = {"D": json.dumps(json_data)}
            response0 = await session.post(url_post, headers=headers, data=form_data)
            # 2
            json_data = {"C":"Gpf_Rpc_Server", "M":"run", "requests":[{"C":"Pap_Affiliates_Reports_TrendsReportWidget", "M":"load", "isInitRequest":"Y", "filterType":"trends_report", "filters":[["datetime","DP","L30D"]]},{"C":"Pap_Stats_TransactionTypes", "M":"getActionTypes", "filters":[["datetime","DP","L30D"]]}], 
                        "S":affiliates_pap_sid}
            form_data = {"D": json.dumps(json_data)}
            response0 = await session.post(url_post, headers=headers, data=form_data)
            def clean_html(html_content):
                cleaned_html = html_content.replace('\\t', '').replace('\\n', '')
                cleaned_html = cleaned_html.replace('\/', '').replace('\\', '').replace('  ', ' ')
                return cleaned_html
            # All time report
            json_data = {"C":"Gpf_Rpc_Server", "M":"run", "requests":[{"C":"Pap_Affiliates_Reports_TrendsReportWidget", "M":"load", "isInitRequest":"Y", "filterType":"trends_report"},{"C":"Pap_Stats_TransactionTypes", "M":"getActionTypes"}], 
                        "S":affiliates_pap_sid}
            form_data = {"D": json.dumps(json_data)}
            response_html_1 = await session.post(url_post, headers=headers, data=form_data)
            # Crawl data
            # print(await response_html_1.text())
            cleaned_html_1 = clean_html(await response_html_1.text())
            soup = BeautifulSoup(cleaned_html_1, 'html.parser')
            # # Lấy thông tin cho từng class 'row'
            rows = soup.find_all('div', class_='row')
            data_crawl = {}
            # Lặp qua từng dòng và lấy thông tin
            row1 = rows[1].text.replace("\u200e","").strip()
            # Get index of Clicks , All clicks , CTR , Totals , Commissions
            clicks_idx = row1.index("Clicks")
            totals_idx = row1.index("Totals")
            blank_idx = row1.index(" ")
            # Hard core with string
            # Đã lấy được value clicks
            string_clicks = row1[clicks_idx:blank_idx] # string clicks
            value_clicks = string_clicks[string_clicks.index("s")+1:]
            # print(value_clicks)
            # print(len(value_clicks))
            data_crawl['Clicks'] = value_clicks
            # value totals
            string_totals = row1[totals_idx:] # split string to get data Totals
            dollar_idx = string_totals.index("$")
            commissions_idx = string_totals.index("Commissions")
            # print(string_totals)
            value_totals = string_totals[dollar_idx:commissions_idx]
            # print(value_totals)
            data_crawl['Totals'] = value_totals
            # print(data_crawl)
            # All time Sales
            json_data = {"C":"Gpf_Rpc_Server", "M":"run", "requests":[{"C":"Pap_Affiliates_Reports_TrendsReportActionWidget", "M":"load", "filters":[["action","E","S"]]}], 
                        "S":affiliates_pap_sid}
            form_data = {"D": json.dumps(json_data)}
            response_html_2 = await session.post(url_post, headers=headers, data=form_data)
            # print(response_html_2.status)
            # print(response_html_2.text)
            # Crawl data
            cleaned_html_2 = clean_html(await response_html_2.text())
            # print(await response_html_2.text())
            soup = BeautifulSoup(cleaned_html_2, 'html.parser')
            rows = soup.find_all('div', class_='row')
            row0 = rows[0].text.replace("\u200e","").strip()
            # print(row0)
            sales_idx = row0.index("Sales")
            fixed_idx = row0.index("Fixed")
            dollar_idx = row0.index("$")
            value_sale_1 = row0[:sales_idx]
            # print(value_sale_1)
            value_sale_2 = row0[dollar_idx:fixed_idx].strip()
            # print(value_sale_2)
            data_crawl['Sales'] = [value_sale_1, value_sale_2]
            return data_crawl

class AffiliatlyComCrawler(Crawler):
    def __init__(self, url, username, password) -> None:
        super().__init__(url, username, password)
       
    async def crawl_data_html(self, html_content):
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
    
    async def crawl(self):
        async with aiohttp.ClientSession() as session:
            url = f"{self.url}/af-1040475/affiliate.panel"
            async with session.get(url, headers=self.default_headers) as response:
                ssid = response.cookies.get('PHPSESSID')
                soup = BeautifulSoup(await response.text(), 'html.parser')
                login_hsf_input = soup.find('input', {'name': 'login_hsf'})
                login_hsf_value = login_hsf_input['value'] if login_hsf_input else None
                login_hsf_time_input = soup.find('input', {'name': 'login_hsf_time'})
                login_hsf_time_value = login_hsf_time_input['value'] if login_hsf_time_input else None

            url = f"{self.url}/af-1040475/affiliate.panel"
            payload = {
                'email': self.username,
                'password': self.password,
                'captcha': '',
                'login_hsf': login_hsf_value,
                'login_hsf_time': login_hsf_time_value,
                'login': ''
            }

            async with session.post(url, headers=self.default_headers, data=payload) as response:
                _affiliatly_logged = session.cookie_jar.filter_cookies(url).get("_affiliatly_logged").value
                # print(_affiliatly_logged)
                if _affiliatly_logged is not None:
                    headers = self.default_headers
                    headers['Cookie'] = f'PHPSESSID={ssid}; _affiliatly_logged={_affiliatly_logged}'
                    url = f"{self.url}/af-1040475/affiliate.panel"
                    async with session.get(url, headers=headers) as response:
                        return await self.crawl_data_html(await response.text())
                else:
                    return f"Error with login website , {self.url}"