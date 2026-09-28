import bs4
import csv
import io
import requests
import re
import datetime
import pytz


def gettitle(url: str) -> str:

    import urllib.request
    import json
    import urllib

    params = {"format": "json", "url": url}
    baseurl = "https://www.youtube.com/oembed"
    query_string = urllib.parse.urlencode(params)
    furl = baseurl + "?" + query_string

    with urllib.request.urlopen(furl) as response:
        response_text = response.read()
        data = json.loads(response_text.decode())
    return data['title']


def getLiveInfo(url: str = "https://schedule.hololive.tv/simple",
                need_title: bool = False):
    # set header in order to post timezone cookie
    headers = {
        "cookie":
        "timezone=Asia/Taipei",
        "User-Agent":
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/115.0.0.0 Safari/537.36"
    }
    # get the webpage
    htmls = requests.get(url, headers=headers)
    # create a soup object
    soup = bs4.BeautifulSoup(htmls.text, 'html.parser')
    # find the live time information by search all html url in the page
    time_info = soup.find_all("div", "row no-gutters")
    url_info = soup.find_all("a")

    liveTime = [
        time_info[i].get_text().replace('\n', '').replace(' ', '')
        for i in range(len(time_info)) if time_info[i].get("class") is not None
    ]
    liveUrl = [url_info[i].get("href") for i in range(len(url_info))]

    pattern_name = r'(?=\d{2}:\d{2})'
    pattern_date = r'\r\d{2}/\d{2}\r\([^)]+\)\r'
    res = []

    sep_date = re.split(pattern_date, liveTime[0])[1:]

    url_count = 9
    title_count = 0
    for i in range(len(sep_date)):
        sep_idol = re.split(pattern_name, sep_date[i])[1:]
        temp = []
        for j in range(len(sep_idol)):
            if i >= 1 and title_count < 20:

                yttitle = gettitle(liveUrl[url_count])
                title = '(' + yttitle[:30] + ')'
                title_count += 1
            else:
                title = ""
            temp.append(
                (sep_idol[j].replace('\r', ' ') + title, liveUrl[url_count]))
            url_count += 1
        res.append(temp)
    return res


def getSchedule(url: str = "https://schedule.hololive.tv/simple/hololive",
                need_title: bool = False):
    info = getLiveInfo(url, need_title)
    tw = pytz.timezone('Asia/Taipei')
    # get current day, only month and day
    today = datetime.datetime.now(tw).strftime("%m/%d")
    # get yesterday, only month and day
    yesterday = (datetime.datetime.now(tw) -
                 datetime.timedelta(days=1)).strftime("%m/%d")
    # get tomorrow, only month and day
    tomorrow = (datetime.datetime.now(tw) +
                datetime.timedelta(days=1)).strftime("%m/%d")
    dates = [yesterday, today, tomorrow]
    res = ""

    for i in range(min(len(dates), len(info))):
        res += dates[i] + "\n"

        for j in range(len(info[i])):
            res += info[i][j][0] + " " + info[i][j][1] + "\n"
        res += "\n"
    return res


BOT_RATE_URL = "https://rate.bot.com.tw/xrt"
BOT_RATE_CSV_URL = "https://rate.bot.com.tw/xrt/flcsv/0/day"
RATE_HEADERS = {
    "User-Agent":
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/115.0.0.0 Safari/537.36"
}
CURRENCY_NAMES = {
    "USD": "美金",
    "HKD": "港幣",
    "GBP": "英鎊",
    "AUD": "澳幣",
    "CAD": "加拿大幣",
    "SGD": "新加坡幣",
    "CHF": "瑞士法郎",
    "JPY": "日圓",
    "ZAR": "南非幣",
    "SEK": "瑞典幣",
    "NZD": "紐元",
    "THB": "泰幣",
    "PHP": "菲國比索",
    "IDR": "印尼幣",
    "EUR": "歐元",
    "KRW": "韓元",
    "VND": "越南盾",
    "MYR": "馬來幣",
    "CNY": "人民幣",
}


def _clean_rate(value: str) -> str:
    # the bank uses "-" or 0 for rates it does not offer
    value = value.strip()
    try:
        if float(value) == 0:
            return "-"
    except ValueError:
        return "-"
    return value.rstrip("0").rstrip(".") if "." in value else value


def _parse_rate_csv(text: str) -> list:
    # each row: code, 本行買入, cash, spot, forwards..., 本行賣出, cash, spot, forwards...
    rates = []
    for row in csv.reader(io.StringIO(text.lstrip("\ufeff"))):
        row = [col.strip() for col in row]
        if "本行買入" not in row or "本行賣出" not in row:
            continue
        buy, sell = row.index("本行買入"), row.index("本行賣出")
        rates.append((row[0], row[buy + 1], row[sell + 1], row[buy + 2],
                      row[sell + 2]))
    return rates


def _parse_rate_html(text: str) -> list:
    # fallback: read the table cells by their data-table column names
    soup = bs4.BeautifulSoup(text, 'html.parser')
    rates = []
    for tr in soup.select("table tbody tr"):
        cells = {
            td.get("data-table"): td
            for td in tr.find_all("td") if td.get("data-table")
        }
        cur = cells.get("幣別")
        if cur is None:
            continue
        match = re.search(r"\(([A-Z]{3})\)", cur.get_text())
        if match is None:
            continue
        rates.append((match.group(1), ) + tuple(
            cells[col].get_text(strip=True) if col in cells else "-"
            for col in ["本行現金買入", "本行現金賣出", "本行即期買入", "本行即期賣出"]))
    return rates


def exchange_rate():
    # (code, cash buy, cash sell, spot buy, spot sell)
    rates = []
    try:
        resp = requests.get(BOT_RATE_CSV_URL, headers=RATE_HEADERS, timeout=10)
        resp.raise_for_status()
        rates = _parse_rate_csv(resp.content.decode("utf-8-sig"))
    except requests.RequestException:
        pass

    if not rates:
        resp = requests.get(BOT_RATE_URL, headers=RATE_HEADERS, timeout=10)
        resp.raise_for_status()
        resp.encoding = "utf-8"
        rates = _parse_rate_html(resp.text)

    if not rates:
        return "目前無法取得臺灣銀行匯率，請稍後再試\n" + BOT_RATE_URL

    res_str = "臺灣銀行牌告匯率 (買入/賣出)\n"
    for code, cash_buy, cash_sell, spot_buy, spot_sell in rates:
        res_str += "{}({})  即期 {}/{}  現金 {}/{}\n".format(
            CURRENCY_NAMES.get(code, code), code, _clean_rate(spot_buy),
            _clean_rate(spot_sell), _clean_rate(cash_buy),
            _clean_rate(cash_sell))

    return res_str.rstrip("\n")
