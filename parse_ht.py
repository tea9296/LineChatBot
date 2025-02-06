import bs4
import requests
import re
import datetime


def getLiveInfo(url: str = "https://schedule.hololive.tv/simple"):
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
    pattern_date = pattern = r'\r\d{2}/\d{2}\r\([^)]+\)\r'
    res = []

    sep_date = re.split(pattern_date, liveTime[0])[1:]

    url_count = 8
    for i in range(len(sep_date)):
        sep_idol = re.split(pattern_name, sep_date[i])[1:]
        temp = []
        for j in range(len(sep_idol)):

            gettitle = requests.get(liveUrl[url_count])
            stt = bs4.BeautifulSoup(gettitle.text, 'html.parser')
            title = str(stt.find_all(name="title")[0]).replace('<title>',
                                                               '')[:20]

            temp.append((sep_idol[j].replace('\r',
                                             ' '), title, liveUrl[url_count]))
            url_count += 1
        res.append(temp)
    return res


def getSchedule(url: str = "https://schedule.hololive.tv/simple/hololive"):
    info = getLiveInfo(url)
    # get current day, only month and day
    today = datetime.datetime.now().strftime("%m/%d")
    # get yesterday, only month and day
    yesterday = (datetime.datetime.now() -
                 datetime.timedelta(days=1)).strftime("%m/%d")
    # get tomorrow, only month and day
    tomorrow = (datetime.datetime.now() +
                datetime.timedelta(days=1)).strftime("%m/%d")
    dates = [yesterday, today, tomorrow]

    res = ""

    for i in range(min(len(dates), len(info))):
        res += dates[i] + "\n"

        for j in range(len(info[i])):
            res += info[i][j][0] + f"({info[i][j][1]}) " + info[i][j][2] + "\n"
        res += "\n"
    return res


def exchange_rate():
    #session = requests_html.HTMLSession()

    #first_page = session.get("https://www.esunbank.com/zh-tw/personal/deposit/rate/forex/foreign-exchange-rates")
    #first_page.html.render(sleep=5)

    # # get the webpage
    htmls = requests.get("https://rate.bot.com.tw/xrt")
    # create a soup object
    soup = bs4.BeautifulSoup(htmls.text, 'html.parser')
    # find the live time information by search all html url in the page
    current_info = soup.find_all(
        "td", "text-right display_none_print_show print_width")
    country_info = soup.find_all("div",
                                 "hidden-phone print_show xrt-cur-indent")

    res_str = "       即期買入      即期賣出\n"
    for i in range(0, len(current_info), 4):
        clean_country = country_info[i // 4].get_text().replace(
            ' ', '').replace('\r', '').replace('\n', '')
        res_str += (clean_country + "      " + current_info[i + 2].get_text() +
                    "      " + current_info[i + 3].get_text() + "\n")

    return res_str


print(getSchedule())
