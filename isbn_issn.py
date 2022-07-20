# -*- coding: utf-8 -*-
from bs4 import BeautifulSoup
import requests
from datetime import datetime
from github import Github
import os
from pytz import timezone
import re


def wc(url):
    headers = {
        "user-agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_14_6) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/78.0.3904.87 Safari/537.36"}
    html = requests.get(url, headers=headers).text
    soup = BeautifulSoup(html, "lxml")
    return soup


def pagecheck(url):
    soup = wc(url)
    checker = soup.find('div','resultTxt').find('span','themeFC totCnt_span')
    return checker.text.strip()


def main():
    today = datetime.today().strftime("%Y-%m-%d")
    page = 1
    checker = pagecheck(f'https://www.nl.go.kr/seoji/contents/S80100000000.do?page=1&pageUnit=100&schType=detail&sort=publish_predate+desc&f1=title&and1=AND&f2=author&and2=AND&f3=publisher&f5=isbn&f7=kdc&v8s={today}&v8e={today}&ebookYn=N')
    global title
    result = ''
    while 1:
        soup = wc(f'https://www.nl.go.kr/seoji/contents/S80100000000.do?page={page}&pageUnit=100&schType=detail&sort=publish_predate+desc&f1=title&and1=AND&f2=author&and2=AND&f3=publisher&f5=isbn&f7=kdc&v8s={today}&v8e={today}&ebookYn=N')
        detail = soup.find_all('div','resultInfo')

        for i in detail:
            title = i.find('a').text.strip()
            # stat = [x.text.strip() for x in i.find('ul')]
            # stat = ' '.join(stat)
            link = i.find('a').get('onclick')
            relink = re.findall(r'\d+', link)
            reurl = f"https://www.nl.go.kr/seoji/contents/S80100000000.do?schM=intgr_detail_view_isbn&page=1&pageUnit=100&schType=detail&sort=publish_predate+desc&f1=title&and1=AND&f2=author&and2=AND&f3=publisher&f5=isbn&f7=kdc&v8s={today}&v8e={today}&ebookYn=N&isbn={relink[0]}&cipId={relink[1]}%2C"
            #result += f"<a href={reurl}>" + title +"</a>"+"<br/>\n"
            #result += f"[{title}]({reurl})\n"
            result += f"{title}\n"
        if f'{checker}.' in title:
            return result
        page += 1


def issueUpload():
    seoul_timezone = timezone('Asia/Seoul')
    today = datetime.now(seoul_timezone)
    tm = today.strftime('%Y-%m-%d')

    uploadText = main()

    access_token = os.environ['MY_GITHUB_TOKEN']
    g = Github(access_token)
    repo = g.get_user().get_repo('ISBN-CIP-scrapping')
    repo.create_issue(title=f"{tm} 발매(예정)일 목록", body=uploadText)


if __name__ == '__main__':
    issueUpload()
