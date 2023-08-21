import bs4 
import requests
import re
import datetime


def getLiveInfo(url:str="https://schedule.hololive.tv/simple"):
    # get the webpage
    htmls = requests.get(url)
    # create a soup object
    soup = bs4.BeautifulSoup(htmls.text, 'html.parser')
    # find the live time information by search all html url in the page
    time_info = soup.find_all("div", "row no-gutters" )
    url_info = soup.find_all("a")

    liveTime =  [time_info[i].get_text().replace('\n','').replace(' ','') for i in range(len(time_info)) if time_info[i].get("class") is not None]
    liveUrl = [url_info[i].get("href") for i in range(len(url_info))]


    pattern_name = r'(?=\d{2}:\d{2})'
    pattern_date = pattern = r'\r\d{2}/\d{2}\r\([^)]+\)\r'
    res = []

    sep_date = re.split(pattern_date,liveTime[0])[1:]
    
    url_count = 8
    for i in range(len(sep_date)):
        sep_idol = re.split(pattern_name,sep_date[i])[1:]
        temp = []
        for j in range(len(sep_idol)):
            temp.append((sep_idol[j].replace('\r',''),liveUrl[url_count]))
            url_count += 1
        res.append(temp)
    return res


def getSchedule(url:str="https://schedule.hololive.tv/simple/hololive"):
    info = getLiveInfo(url)

    # get current day, only month and day
    today = datetime.datetime.now().strftime("%m/%d")
    # get yesterday, only month and day
    yesterday = (datetime.datetime.now() - datetime.timedelta(days=1)).strftime("%m/%d")
    # get tomorrow, only month and day
    tomorrow = (datetime.datetime.now() + datetime.timedelta(days=1)).strftime("%m/%d")
    dates = [yesterday, today, tomorrow]

    res = ""

    for i in range(len(dates)):
        res += dates[i] + "\n"
        for j in range(len(info[i])):
            res += info[i][j][0] + " " + info[i][j][1] + "\n"
        res += "\n"
    return res


