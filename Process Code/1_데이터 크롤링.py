# -*- coding: utf-8 -*-
"""
스팀 리뷰 데이터 크롤링 코드

"""
from selenium import webdriver
import time
import requests
import re
from bs4 import BeautifulSoup
import pandas as pd

#%%

class Steam:
    def __init__(self, game_id, cond):
        self.game_id = game_id  # steam game code
        self.cond = cond  # positive or negative only

    def get_review(self):
        browser = webdriver.Chrome(
            "C:\\Users\\korea\\OneDrive\\바탕 화면\\캡스톤디자인 프로젝트\\chromedriver_win32\\chromedriver.exe")
        browser.maximize_window()

        # 페이지 이동
        url = "https://steamcommunity.com/app/" + self.game_id + "/" + \
            self.cond + "reviews/?browsefilter=toprated&p=1&filterLanguage=koreana"
        browser.get(url)

        interval = 2  # 2초에 한번씩 스크롤 다운

        # 현재 문서 높이 가져와서 저장
        prev_height = browser.execute_script(
            "return document.body.scrollHeight")

        # 반복수행
        while True:
            # 스크롤을 가장 아래로 내림
            browser.execute_script(
                "window.scrollTo(0, document.body.scrollHeight)")

        # 페이지 로딩 대기
            time.sleep(interval)

        # 현재 문서 높이를 가져와서 저장
            curr_height = browser.execute_script(
                "return document.body.scrollHeight")
            if curr_height == prev_height:
                break

            prev_height = curr_height
        print("스크롤 완료")

        soup = BeautifulSoup(browser.page_source, "lxml")

        # 리뷰, 플레이타임, 리뷰추천수
        review_box = soup.find_all(
            "div", attrs={"class": "apphub_CardContentMain"})
        print(len(review_box))

        df_review = []
        df_playtime = []
        df_helpful = []
        df_funny = []
        df_game_cnt = []
        df_date_year = []
        df_date_month = []

        year = ['2000', '2001', '2002', '2003', '2004', '2005', '2006', '2007', '2008', '2009', '2010',
                '2011', '2012', '2013', '2014', '2015', '2016', '2017', '2018', '2019', '2020', '2021']
        month = ['January', 'February', 'March', 'April', 'May', 'June', 'July',
                 'August', 'September', 'October', 'November', 'December']

        for box in review_box:
            review = box.find(
                "div", attrs={"class": "apphub_CardTextContent"}).get_text().strip()
            review = review.replace('Early Access Review', '')
            review = review.replace('Posted: ', '')
            review = review.split()
            if len(review) == 2:
                pass
            else:
                if (review[2] in year):
                    review = ' '.join(review[3:])
                else:
                    review = ' '.join(review[2:])
            df_review.append(review)

            playtime = box.find("div", attrs={"class": "hours"}).get_text()
            playtime = playtime.split()
            temp1 = []
            for w in playtime:
                w = re.sub(r'[^0-9.]', '', w)
                w = "".join([str(_) for _ in w])
                temp1.append(w)
            temp1 = list(filter(None, temp1))
            df_playtime.append(float(temp1[0]))

            recommend = box.find(
                "div", attrs={"class": "found_helpful"}).get_text().strip()
            recommend = recommend.split()
            temp2 = []  # 유용한 평가, 재미있는 평가, 받은 이모티콘 수
            for w in recommend:
                w = re.findall(r'[0-9]+', w)
                w = "".join([str(_) for _ in w])
                temp2.append(w)
            temp2 = list(filter(None, temp2))

            if len(temp2) == 3:
                df_helpful.append(int(temp2[0]))
                df_funny.append(int(temp2[1]))
            elif len(temp2) == 2:
                df_helpful.append(int(temp2[0]))
                df_funny.append(int(temp2[1]))
            elif len(temp2) == 1:
                df_helpful.append(int(temp2[0]))
                df_funny.append(int(0))
            else:
                df_helpful.append(int(0))
                df_funny.append(int(0))

            # 리뷰 게시 일시
            date = box.find("div", attrs={"class": "date_posted"}).get_text()
            date = date.replace('Posted: ', '')
            date = date.replace(',', '')
            date = date.split()
            
            get_i = 0
            for i in range(len(date)):  # 년도 추출
                if date[i] in year:
                    get_i = i
            if get_i:
                df_date_year.append(date[get_i])
            else:
                df_date_year.append(2021)
            
            get_i = 0
            for i in range(len(date)):  # 월 추출
                if date[i] in month:
                    df_date_month.append(date[i])

        # 구매한 게임 수
        games = soup.find_all(
            "div", attrs={"class": "apphub_CardContentAuthorBlock tall"})

        for game in games:
            game_cnt = game.find(
                "div", attrs={"class": "apphub_CardContentMoreLink ellipsis"}).get_text()
            game_cnt = re.sub(r'[^0-9]', '', game_cnt)
            df_game_cnt.append(game_cnt)
            

        final_data = {'리뷰': df_review, "플레이타임": df_playtime,
                      '유용한 평가': df_helpful, '재밌는 평가': df_funny, 
                      '구매게임 수': df_game_cnt, '작성 년도': df_date_year, '작성 월': df_date_month}
        df = pd.DataFrame(final_data)
        
        df['작성 월'] = df['작성 월'].map({'January':1, 'February':2, 'March':3, 'April':4, 'May':5, 'June':6, 'July':7,
                 'August':8, 'September':9, 'October':10, 'November':11, 'December':12})

        # positive : 1  / negative : 0
        if self.cond == 'positive':
            df['label'] = 1
        else:
            df['label'] = 0
        return df


#%% 스팀게임 ID code를 통해 해당 게임의 리뷰를 크롤링

def review_df(code):  #code = 스팀게임ID
  g_pos = Steam(str(code), 'positive')
  g_r_pos = g_pos.get_review()

  g_neg = Steam(str(code), 'negative')
  g_n_pos = g_neg.get_review()

  new_df = pd.concat([g_r_pos, g_n_pos], ignore_index=True)

  shuffle_df = new_df.sample(frac=1).reset_index(drop=True)
  return shuffle_df