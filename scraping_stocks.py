from bs4 import BeautifulSoup
import requests
import time
import pandas as pd

# this code for scraping all stocks
url = "https://finviz.com/screener.ashx?v=111&o=ticker"
headers = {
    "accept": "*/*",
     "accept-encoding": "gzip, deflate, br",
    "accept-Language": "ru-RU,ru;q=0.9,en-US;q=0.8,en;q=0.7",
    "cache-control": "no-cache",
    "cookie": "_pubcid=07403b35-7bd9-414f-9511-fdc7f3792511; __qca=P0-1570853545-1678089153162; _gd_visitor=f1fd7d11-3d44-46f4-8416-c5fd30dddd2b; _cc_id=3ebd00da1aac35a34d14f1b47b8ca508; _gd_svisitor=3f85655f8f550000c19b0564d5030000e8d14a00; _admrla=2.2-4994a3e2bfe24997-8f6230af-bcb5-11ed-ad71-c74812dfbfa4; cto_bidid=guwT5F8wOXUlMkJPMmpYYTFkdXBzY3NqU1B2RWRtSXB5Q0hWblJYUHNTaFVxY0tRZ2xYTnAlMkJUQTM5eDRTN3pXOE9rVlJBJTJGTFFrZUVvV0R6V2hPMlEyVjBrZGI3JTJCcnRjdXFhampmTmF1TlBBM1MlMkYlMkZRSEdnOVhqQUJ3Tzk0Z1NpaHZLSHVuOUhqdlRzSlRSVklQalBnaUttJTJCdFVNUSUzRCUzRA; _awl=2.1678282379.5-e6f27f55b6ca473ef5d63faaa3a2521e-6763652d6575726f70652d7765737431-0; cto_bundle=bh8uTl9rZXE5NWdmNENOSnFUSyUyQlp2b2FtMk9ZSG9kOXczc0FjUTI3WHVkWGFhUTNzNkN4ZmRXeWkxbE1YRDlUbTc1aHVucGZGVDJyY3pUUnZPYXhJakRRMkRjNFZMV3FEOVFBOCUyQkZlRHp4eExZa3pzeXJoMWclMkJiJTJGdTRxemMzQ2ttdnIlMkZZUnRtMjVrY29JU1dJU3NCSUQ1TGV2aDBybWVDTW1VUVI0cDJXYVE1dGZ1ZXdET0RkN2VzV1JXbU13Qld2MWow; chartsTheme=dark; _gid=GA1.2.88193917.1684817905; pv_date=Tue May 23 2023 07:58:29 GMT+0300 (Moscow Standard Time); fv_block=block; screenerUrl=screener.ashx%3Fv%3D111%26f%3Dfa_estltgrowth_pos%2Cfa_pe_u40%2Cfa_roe_pos%2Cfa_roi_pos%2Cfa_sales5years_pos%26ft%3D2%26o%3D-marketcap; pv_count=10; _gat_gtag_UA_3261808_1=1; _ga=GA1.1.682959199.1678089153; _ga_ZT9VQEWD4N=GS1.1.1684817904.6.1.1684819627.0.0.0",
    "origin":
        "https://finviz.com", "pragma":
"no-cache",
        "sec-ch-ua":
'"Google Chrome";v="113", "Chromium";v="113", "Not-A.Brand";v="24"',
"sec-ch-ua-mobile": "?0",
"sec-ch-ua-platform": "macOS",
    "sec-fetch-dest": "script",
    "sec-fetch-mode": "cors",
    "sec-fetch-site": "cross-site",
    "user-agent":
        "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/113.0.0.0 Safari/537.36"}


r = requests.get(url, headers = headers)
soup = BeautifulSoup(r.content, 'html.parser')
s = soup.find('table', class_ = "table-light")

soup_urls = []
def make_soup(url):
    r = requests.get(url, headers = headers)
    soup = BeautifulSoup(r.content, 'html.parser')
    s = soup.find('table', class_ = "table-light")
    return s
soup_urls.append(make_soup(url))

num = 2

for i in range(412):
    time.sleep(3)
    url_to_use = url + "&r=" + str(num) + "1"
    num += 2
    s = make_soup(url_to_use)
    soup_urls.append(s)


def make_text_cap(num):
    if num[-1] == 'M' or num == '-':
        return 'Small or Mid Cap'

    num = num[:len(num) - 1]
    num = float(num)

    if num > 10:
        return 'Large Cap'
    else:
        return 'Small or Mid Cap'

stocks = pd.DataFrame(data={"Ticker": [], "Country": [], "Cap": []})
i = 0

for s in soup_urls:
    rows = s.find_all('tr')
    rows = rows[1:] # excluding the header

    for row in rows:
        item = row.find_all('td')
        cap = make_text_cap(item[6].text)
        stocks.loc[i] = [item[1].text, item[5].text, cap]
        i += 1

us_treasuries_t = ['TNX', 'IRX', 'TYX', 'FVX']
for j in range(len(us_treasuries_t)):
    stocks.loc[i+1] = [us_treasuries_t[j], '', '']
    i += 1


# this code for scraping recommended stocks
url = "https://finviz.com/screener.ashx?v=111&f=fa_estltgrowth_pos,fa_pe_u40,fa_roe_pos,fa_roi_pos,fa_sales5years_pos&ft=2&r=1"

headers = {
    "accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.9",
"accept-encoding": "gzip, deflate, br",
"accept-language": "ru-RU,ru;q=0.9,en-US;q=0.8,en;q=0.7",
"cache-control": "max-age=0",
"cookie": "screenerUrl=screener.ashx%3Fv%3D111%26f%3Dfa_estltgrowth_pos%2Cfa_pe_u40%2Cfa_roe_pos%2Cfa_roi_pos%2Cfa_sales5years_pos%26ft%3D2; pv_date=Mon Mar 06 2023 10:52:32 GMT+0300 (Moscow Standard Time); pv_count=1; _ga=GA1.2.682959199.1678089153; _gid=GA1.2.1916108864.1678089153; usprivacy=1---; IC_ViewCounter_finviz.com=1; _pbjs_userid_consent_data=3524755945110770; _pubcid=07403b35-7bd9-414f-9511-fdc7f3792511; _lr_retry_request=true; _lr_env_src_ats=false; __qca=P0-1570853545-1678089153162; _gd_visitor=f1fd7d11-3d44-46f4-8416-c5fd30dddd2b; _gd_session=97afc26f-2fe4-4621-8e6e-9bd6f4cd1134; _an_uid=0; pbjs-unifiedid=%7B%22TDID%22%3A%2223410cf6-1843-4fde-baff-fa378b55361e%22%2C%22TDID_LOOKUP%22%3A%22TRUE%22%2C%22TDID_CREATED_AT%22%3A%222023-02-06T07%3A52%3A33%22%7D; panoramaId_expiry=1678175553758; _cc_id=3ebd00da1aac35a34d14f1b47b8ca508; cto_bundle=0sW6Vl9rZXE5NWdmNENOSnFUSyUyQlp2b2FtMkhERmR1Nm9DQjJhc3pORlJtVWNDcTdVYVRQTnB5JTJCVWpEb01rOUNiQVZ1RTRsajNpZ2Njd2xmcUFETDdLVVBhMmFYeXJzUWRrTHFUS1BOcCUyQlFaeVhSZGN5ZEtOQlZLRlVRNUdKNFdlazB3OGlCajFXUmlDV0wxSHVZbVBBYlpPOW1VNUhVUkJOcXlKMXVHcmJFOFRSUktXeDMzSnE3ViUyRmJKaFZVSHIwNE1MZQ; cto_bidid=5BvL5l8wOXUlMkJPMmpYYTFkdXBzY3NqU1B2RWRtSXB5Q0hWblJYUHNTaFVxY0tRZ2xYTnAlMkJUQTM5eDRTN3pXOE9rVlJBJTJGRmxrUG1nQXNnNVVVNUFVd0dTb2lMWkgydmkweVZzV2hpVmtRbHkwNWlnalZkUFcxcUkxczQlMkJQUlpPdkY2cmFhZjIlMkJIaTJNJTJCbWpHTE8lMkJ5RG1WRW9CQSUzRCUzRA; fv_block=block; _ga_ZT9VQEWD4N=GS1.1.1678089153.1.0.1678089175.0.0.0",
"sec-ch-ua": '"Not_A Brand";v="99", "Google Chrome";v="109", "Chromium";v="109"',
"sec-ch-ua-mobile": "?0",
"sec-ch-ua-platform": "macOS",
"sec-fetch-dest": "document",
"sec-fetch-mode": "navigate",
"sec-fetch-site": "none",
"sec-fetch-user": "?1",
"upgrade-insecure-requests": "1",
"user-agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/109.0.0.0 Safari/537.36"
}

soup_urls = []


def make_soup(url_soup):
    r = requests.get(url_soup, headers=headers)
    soup = BeautifulSoup(r.content, 'html.parser')
    ms = soup.find('table', class_="table-light")
    return ms


soup_urls.append(make_soup(url))

num = 2

for i in range(59):
    time.sleep(3)
    url_to_use = url[:len(url) - 1] + str(num) + "1"
    num += 2
    s = make_soup(url_to_use)
    soup_urls.append(s)
    if len(s) == 0:
        print(num)
        break


rec_stocks = {"Ticker": [], "Sector": [], "Country": [], "Cap": [], "P/E": []}
rec_stocks = pd.DataFrame(data=rec_stocks)
i = 0

for s in soup_urls:
    rows = s.find_all('tr')
    rows = rows[1:]  # excluding the header

    for row in rows:
        item = row.find_all('td')
        cap = make_text_cap(item[6].text)
        rec_stocks.loc[i] = [item[1].text, item[3].text, item[5].text, cap, item[7].text]
        i += 1
