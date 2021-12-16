# -*- coding: utf-8 -*-
"""
Created on Thu Dec 16 12:12:46 2021

@author: user
"""
# 한글 폰트 설정
!sudo apt-get install -y fonts-nanum
!sudo fc-cache -fv
!rm ~/.cache/matplotlib -rf

import matplotlib.pyplot as plt

plt.rc('font', family='NanumBarunGothic') 

#%%
#크롤링 라이브러리 설치
!pip install selenium
!apt-get update
!apt install chromium-chromedriver
!cp /usr/lib/chromium-browser/chromedriver /usr/bin

#%%
# 필요한 라이브러리 및 환경 설정
from selenium import webdriver
from urllib.request import urlopen
from bs4 import BeautifulSoup 
from urllib.parse import quote_plus
from selenium.webdriver.common.keys import Keys
import time
import pandas as pd
import re
import requests
import numpy as np

pd.set_option('display.max_rows' ,100000)
pd.set_option('max_colwidth',100000)

#%%
# 크롤링 class
class Steam:
    def __init__(self, game_id, cond):
        self.game_id = game_id  # steam game code
        self.cond = cond  # positive or negative only

    def get_review(self):
        options = webdriver.ChromeOptions()
        options.add_argument('--headless')        # Head-less 설정
        options.add_argument('--no-sandbox')
        options.add_argument('--disable-dev-shm-usage')
        browser = webdriver.Chrome('chromedriver', options=options)
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

#%%
# 긍정 부정 리뷰 크롤링 후 랜덤 셔플링 후 데이터프레임화
def review_df(code):
  g_pos = Steam(str(code), 'positive')
  g_r_pos = g_pos.get_review()

  g_neg = Steam(str(code), 'negative')
  g_n_pos = g_neg.get_review()

  new_df = pd.concat([g_r_pos, g_n_pos], ignore_index=True)

  shuffle_df = new_df.sample(frac=1).reset_index(drop=True)
  return shuffle_df

temp = review_df(582010) #582010 코드의 게임 리뷰 크롤링

#%%
### 전처리 ###
df = temp.copy()

# 이모티콘 제거
import re

emoji_pattern = re.compile("["
        u"\U0001F600-\U0001F64F"  # emoticons
        u"\U0001F300-\U0001F5FF"  # symbols & pictographs
        u"\U0001F680-\U0001F6FF"  # transport & map symbols
        u"\U0001F1E0-\U0001F1FF"  # flags (iOS)
                           "]+", flags=re.UNICODE)
for i in range(len(df)):
  df['리뷰'][i] = emoji_pattern.sub(r'', df['리뷰'][i])


# 특수문자 제거
characters1 = "\\"
characters2 = "\u200b5."
characters3 = "\u200b4."
characters4 = "\u200b" 
characters5 = "\'"
characters6 = '\U0001f7e9'

for i in range(len(df)):
  df['리뷰'][i] = df['리뷰'][i].replace(characters1,"")
  df['리뷰'][i] = df['리뷰'][i].replace(characters2,"")
  df['리뷰'][i] = df['리뷰'][i].replace(characters3,"")
  df['리뷰'][i] = df['리뷰'][i].replace(characters4,"")
  df['리뷰'][i] = df['리뷰'][i].replace(characters5,"")
  
# 반복 문자 normalization
!pip install soynlp

from soynlp.normalizer import *

for idx in range(len(df)): 
  df['리뷰'][i] = repeat_normalize(df['리뷰'][i], num_repeats=2)
  
# 문장 분리
!pip install kss
df_kss = pd.DataFrame(columns=['리뷰', '플레이타임', '유용한 평가', '재밌는 평가'	,'구매게임 수','작성 년도', '작성 월', 'label'])

from tqdm import tqdm
import kss
df_kss_idx = 0

for idx in tqdm(range(len(df))):
  # 분리된 문장 리스트에 담기
  sentence_tokenized_review = []
  
  if '☐' in df['리뷰'][idx]:
    sentence_tokenized_review.append(df['리뷰'][idx])
  else:
    for sent in kss.split_sentences(df['리뷰'][idx]):
      sentence_tokenized_review.append(sent.strip())

  # 분리된 문장 다시 데이터프레임에 추가 정보와 함께 담기
  for i in range(len(sentence_tokenized_review)):
    df_kss.loc[df_kss_idx] = [sentence_tokenized_review[i],df['플레이타임'][idx], df['유용한 평가'][idx], df['재밌는 평가'][idx], df['구매게임 수'][idx],df['작성 년도'][idx], df['작성 월'][idx], df['label'][idx]]
    df_kss_idx +=1

#%%
### 속성어 사전으로 리뷰 평가 분류
# 사운드 속성어사전
dic_sound_url = 'https://raw.githubusercontent.com/kimbyeolhee/Steam-review/main/%EC%86%8D%EC%84%B1%EC%96%B4%EC%82%AC%EC%A0%84/%EC%82%AC%EC%9A%B4%EB%93%9C/%EC%82%AC%EC%9A%B4%EB%93%9C_%EC%86%8D%EC%84%B1%EC%96%B4%EC%82%AC%EC%A0%84.txt'
dic_sound = pd.read_csv(dic_sound_url, sep='\t', index_col = False)

list_sound = [dic_sound['속성어'][i] for i in range(len(dic_sound))]

# 유저서비스 속성어사전
dic_US_url = 'https://raw.githubusercontent.com/kimbyeolhee/Steam-review/main/%EC%86%8D%EC%84%B1%EC%96%B4%EC%82%AC%EC%A0%84/%EC%9C%A0%EC%A0%80%EC%84%9C%EB%B9%84%EC%8A%A4/%EC%9C%A0%EC%A0%80%EC%84%9C%EB%B9%84%EC%8A%A4_%EC%86%8D%EC%84%B1%EC%96%B4%EC%82%AC%EC%A0%84.txt'
dic_US = pd.read_csv(dic_US_url, sep='\t', index_col = False)
dic_US.columns =['속성어']

list_us = [dic_US['속성어'][i] for i in range(len(dic_US))]

# 난이도 속성어사전
dic_level_url = 'https://raw.githubusercontent.com/kimbyeolhee/Steam-review/main/%EC%86%8D%EC%84%B1%EC%96%B4%EC%82%AC%EC%A0%84/%EB%82%9C%EC%9D%B4%EB%8F%84/%EB%82%9C%EC%9D%B4%EB%8F%84_%EC%86%8D%EC%84%B1%EC%96%B4%EC%82%AC%EC%A0%84.txt'
dic_level = pd.read_csv(dic_level_url, sep='\t', index_col = False)

list_level = [dic_level['속성어'][i] for i in range(len(dic_level))]

# 그래픽 속성어사전
dic_graphic_url = 'https://raw.githubusercontent.com/kimbyeolhee/Steam-review/main/%EC%86%8D%EC%84%B1%EC%96%B4%EC%82%AC%EC%A0%84/%EA%B7%B8%EB%9E%98%ED%94%BD/%EA%B7%B8%EB%9E%98%ED%94%BD_%EC%86%8D%EC%84%B1%EC%96%B4%EC%82%AC%EC%A0%84.txt'
dic_graphic = pd.read_csv(dic_graphic_url, sep='\t', index_col = False)

list_graphic = [dic_graphic['속성어'][i] for i in range(len(dic_graphic))]

# 플레이 속성어사전
dic_play_url = 'https://raw.githubusercontent.com/kimbyeolhee/Steam-review/main/%EC%86%8D%EC%84%B1%EC%96%B4%EC%82%AC%EC%A0%84/%ED%94%8C%EB%A0%88%EC%9D%B4/%ED%94%8C%EB%A0%88%EC%9D%B4_%EC%86%8D%EC%84%B1%EC%96%B4%EC%82%AC%EC%A0%84.txt'
dic_play = pd.read_csv(dic_play_url, sep='\t', index_col = False)

list_play = [dic_play['속성어'][i] for i in range(len(dic_play))]

# 스토리 속성어사전
dic_story_url = 'https://raw.githubusercontent.com/kimbyeolhee/Steam-review/main/%EC%86%8D%EC%84%B1%EC%96%B4%EC%82%AC%EC%A0%84/%EC%8A%A4%ED%86%A0%EB%A6%AC/%EC%8A%A4%ED%86%A0%EB%A6%AC_%EC%86%8D%EC%84%B1%EC%96%B4%EC%82%AC%EC%A0%84.txt'
dic_story = pd.read_csv(dic_story_url, sep='\t', index_col = False)

list_story = [dic_story['속성어'][i] for i in range(len(dic_story))]

# 속성 평가 리뷰 분류
df_attr_class = pd.DataFrame(columns=['리뷰','사운드','유저서비스','난이도','그래픽','플레이','스토리','플레이타임', '유용한 평가', '재밌는 평가'	,'구매게임 수','작성 년도', '작성 월', 'label'])

for idx in range(len(df_kss)):
  # 속성어 갯수 카운트
  sound_count, US_count, level_count, graphic_count, play_count, story_count = 0, 0, 0, 0, 0, 0

  # 리뷰에서 속성어 확인
  for attr in list_sound:
    sound_count += df_kss['리뷰'][idx].count(attr)
  for attr in list_us:
    US_count += df_kss['리뷰'][idx].count(attr)
  for attr in list_level:
    level_count += df_kss['리뷰'][idx].count(attr)
  for attr in list_graphic:
    graphic_count += df_kss['리뷰'][idx].count(attr)
  for attr in list_play:
    play_count += df_kss['리뷰'][idx].count(attr)
  for attr in list_story:
    story_count += df_kss['리뷰'][idx].count(attr)

  # 결과 데이터프레임에 추가
  df_attr_class.loc[idx] = [df_kss['리뷰'][idx],sound_count, US_count, level_count, graphic_count, play_count, story_count,df_kss['플레이타임'][idx], df_kss['유용한 평가'][idx], df_kss['재밌는 평가'][idx], df_kss['구매게임 수'][idx],df_kss['작성 년도'][idx], df_kss['작성 월'][idx], df_kss['label'][idx]]
  
# 속성 별 데이터프레임
df_sound = pd.DataFrame(columns=['리뷰', '플레이타임', '유용한 평가', '재밌는 평가'	,'구매게임 수','작성 년도', '작성 월', 'label'])
df_us =  pd.DataFrame(columns=['리뷰', '플레이타임', '유용한 평가', '재밌는 평가'	,'구매게임 수','작성 년도', '작성 월', 'label'])
df_level =  pd.DataFrame(columns=['리뷰', '플레이타임', '유용한 평가', '재밌는 평가'	,'구매게임 수','작성 년도', '작성 월', 'label'])
df_graphic =  pd.DataFrame(columns=['리뷰', '플레이타임', '유용한 평가', '재밌는 평가'	,'구매게임 수','작성 년도', '작성 월', 'label'])
df_play =  pd.DataFrame(columns=['리뷰', '플레이타임', '유용한 평가', '재밌는 평가'	,'구매게임 수','작성 년도', '작성 월', 'label'])
df_story =  pd.DataFrame(columns=['리뷰', '플레이타임', '유용한 평가', '재밌는 평가'	,'구매게임 수','작성 년도', '작성 월', 'label'])

for idx in range(len(df_attr_class)):
  sound = df_attr_class['사운드'][idx]
  US = df_attr_class['유저서비스'][idx]
  level = df_attr_class['난이도'][idx]
  graphic = df_attr_class['그래픽'][idx]
  play = df_attr_class['플레이'][idx]
  story = df_attr_class['스토리'][idx]

  nst = [['사운드', sound], ['유저서비스', US], ['난이도',level], ['그래픽',graphic], ['플레이',play], ['스토리',story]]
  col_name, max_value = max(nst, key=lambda item: item[1])

  new_data = {'리뷰': df_attr_class['리뷰'][idx],
              '플레이타임': df_attr_class['플레이타임'][idx],
              '유용한 평가': df_attr_class['유용한 평가'][idx],
              '재밌는 평가': df_attr_class['재밌는 평가'][idx],
              '구매게임 수': df_attr_class['구매게임 수'][idx],
              '작성 년도': df_attr_class['작성 년도'][idx],
              '작성 월': df_attr_class['작성 월'][idx],
              'label': df_attr_class['label'][idx]}

  if max_value == 0: #모두 0값인 것은 제외
    pass

  else:
    if col_name == '사운드':
      df_sound = df_sound.append(new_data,ignore_index=True)
    elif col_name =='유저서비스':
      df_us = df_us.append(new_data,ignore_index=True)
    elif col_name == '난이도':
      df_level = df_level.append(new_data,ignore_index=True)
    elif col_name == '그래픽':
      df_graphic = df_graphic.append(new_data,ignore_index=True)
    elif col_name == '플레이':
      df_play = df_play.append(new_data,ignore_index=True)
    elif col_name == '스토리':
      df_story = df_story.append(new_data,ignore_index=True)
      
### 평가어휘 사전으로 점수 계산
# 라이브러리 설치
!set -x \
&& pip install konlpy \
&& curl -s https://raw.githubusercontent.com/konlpy/konlpy/master/scripts/mecab.sh | bash -x

class Score:
  def __init__(self, text):
    self.text = text
    self.sent = komoran.pos(text)

  def get_score(self):
    score = 0
    neg_disig_score = 0
    t_score = 0
    t_rein = 1

    plus_list = ['VV','VA','XR','NNG','NNP','MAG','EC']
    multiple_list = ['MAG', 'VX', 'NNG','NNB','NNP']

    # 1. 평가 어휘들만 속한 리스트 생성
    eval_list = list()

    for i in range(len(self.sent)):
      temp = eval_dic_komoran.loc[(eval_dic_komoran['word'] == self.sent[i][0]) & (eval_dic_komoran['tag'] == self.sent[i][1])]
      if temp.empty != True:
        eval_list.append(self.sent[i])

    print(eval_list)
    ### '안' + '평가어휘' + '없' ###
    if (('안', 'MAG') in eval_list) & (('없', 'VA') in eval_list):
      idx = eval_list.index(('안', 'MAG'))
      idx2 = eval_list.index(('없', 'VA'))

      if idx + 2 == idx2:

        word1 =  eval_dic_komoran.loc[(eval_dic_komoran['word'] == eval_list[idx][0]) & (eval_dic_komoran['tag'] == eval_list[idx][1])] # 안
        word2 =  eval_dic_komoran.loc[(eval_dic_komoran['word'] == eval_list[idx+1][0]) & (eval_dic_komoran['tag'] == eval_list[idx+1][1])] # 평가어휘
        word3 =  eval_dic_komoran.loc[(eval_dic_komoran['word'] == eval_list[idx+2][0]) & (eval_dic_komoran['tag'] == eval_list[idx+2][1])] # 없

        weight1 = float(word1['reinforcer'].unique())#안없
        weight2 = float(word3['reinforcer'].unique())
        score = float(word2['score'].unique())

        neg_disig_score = (weight1 * weight2) * score

        del eval_list[idx:idx+3]

        for i in range(len(eval_list)):
          temp = eval_dic_komoran.loc[(eval_dic_komoran['word'] == eval_list[i][0]) & (eval_dic_komoran['tag'] == eval_list[i][1])]
          if temp.empty != True:
            score = float(temp['score'].unique())  #안없
            rein = float(temp['reinforcer'].unique())

            word = list(temp.word)[0]

            if eval_list[i][1] in plus_list:
              t_score += score
            if eval_list[i][1] in multiple_list:
              t_rein *= rein
            else:
              pass

    ### '평가어휘' + '없' ###
    # 2. 평가 어휘 리스트에 ('없','VX')가 속한 경우 [앞 평가어휘 점수와 곱한 점수]를 총 점수에 더함
    elif ('없', 'VA') in eval_list:
      idx = eval_list.index(('없', 'VA'))

      if idx == 0:
        del eval_list[idx]  # '없'과 결합한 평가 어휘가 없을 때

        for i in range(len(eval_list)):
          temp = eval_dic_komoran.loc[(eval_dic_komoran['word'] == eval_list[i][0]) & (eval_dic_komoran['tag'] == eval_list[i][1])]
          if temp.empty != True:
            score = float(temp['score'].unique()) #없
            rein = float(temp['reinforcer'].unique())

            word = list(temp.word)[0]

            if eval_list[i][1] in plus_list:
              t_score += score
            if eval_list[i][1] in multiple_list:
              t_rein *= rein
            else:
              pass
              
      elif ('핵','NNG') in eval_list:
        del eval_list[idx]  # '없'과 결합한 평가 어휘가 없을 때

        for i in range(len(eval_list)):
          temp = eval_dic_komoran.loc[(eval_dic_komoran['word'] == eval_list[i][0]) & (eval_dic_komoran['tag'] == eval_list[i][1])]
          if temp.empty != True:
            score = float(temp['score'].unique()) #없
            rein = float(temp['reinforcer'].unique())

            word = list(temp.word)[0]

            if eval_list[i][1] in plus_list:
              t_score += score
            if eval_list[i][1] in multiple_list:
              t_rein *= rein
            else:
              pass

      else:
        word1 =  eval_dic_komoran.loc[(eval_dic_komoran['word'] == eval_list[idx][0]) & (eval_dic_komoran['tag'] == eval_list[idx][1])]  # '없' 평가 점수 데이터프레임
        word2 =  eval_dic_komoran.loc[(eval_dic_komoran['word'] == eval_list[idx-1][0]) & (eval_dic_komoran['tag'] == eval_list[idx-1][1])] # '없' 앞의 평가어휘의 점수 데이터프레임

        weight = float(word1['reinforcer'].unique())#없
        score = float(word2['score'].unique())

        neg_disig_score = weight * score

        # 2-1. 나머지 어휘들의 점수 계산과 합산
        del eval_list[idx-1:idx+1]  # '없'과 '없'과 결합한 평가 어휘를 리스트에서 제거

        for i in range(len(eval_list)):
          temp = eval_dic_komoran.loc[(eval_dic_komoran['word'] == eval_list[i][0]) & (eval_dic_komoran['tag'] == eval_list[i][1])]
          if temp.empty != True:
            score = float(temp['score'].unique()) #없
            rein = float(temp['reinforcer'].unique())

            word = list(temp.word)[0]

            if eval_list[i][1] in plus_list:
              t_score += score
            if eval_list[i][1] in multiple_list:
              t_rein *= rein
            else:
              pass

    ### '평가어휘' + '있' ###
    # 2. 평가 어휘 리스트에 ('없','VX')가 속한 경우 [앞 평가어휘 점수와 곱한 점수]를 총 점수에 더함
    elif ('있', 'VV') in eval_list:
      idx = eval_list.index(('있', 'VV'))

      word1 =  eval_dic_komoran.loc[(eval_dic_komoran['word'] == eval_list[idx][0]) & (eval_dic_komoran['tag'] == eval_list[idx][1])]  # '있' 평가 점수 데이터프레임
      word2 =  eval_dic_komoran.loc[(eval_dic_komoran['word'] == eval_list[idx-1][0]) & (eval_dic_komoran['tag'] == eval_list[idx-1][1])] # '있' 앞의 평가어휘의 점수 데이터프레임

      weight = float(word1['reinforcer'].unique())#있
      score = float(word2['score'].unique())

      neg_disig_score = weight * score

      # 2-1. 나머지 어휘들의 점수 계산과 합산
      del eval_list[idx-1:idx+1]  # '않'과 '않'과 결합한 평가 어휘를 리스트에서 제거

      for i in range(len(eval_list)):
        temp = eval_dic_komoran.loc[(eval_dic_komoran['word'] == eval_list[i][0]) & (eval_dic_komoran['tag'] == eval_list[i][1])]
        if temp.empty != True:
          score = float(temp['score'].unique()) #있
          rein = float(temp['reinforcer'].unique())

          word = list(temp.word)[0]

          if eval_list[i][1] in plus_list:
            t_score += score
          if eval_list[i][1] in multiple_list:
            t_rein *= rein
          else:
            pass

    ### '평가어휘' + '않' ###  
    # 2. 평가 어휘 리스트에 ('않','VX')가 속한 경우 [앞 평가어휘 점수와 곱한 점수]를 총 점수에 더함
    elif ('않', 'VX') in eval_list:
      idx = eval_list.index(('않', 'VX')) # '않'의 index

      if idx == 0:
        del eval_list[idx]

        for i in range(len(eval_list)):
          temp = eval_dic_komoran.loc[(eval_dic_komoran['word'] == eval_list[i][0]) & (eval_dic_komoran['tag'] == eval_list[i][1])]
          if temp.empty != True:
            score = float(temp['score'].unique())  #않
            rein = float(temp['reinforcer'].unique())

            word = list(temp.word)[0]

            if eval_list[i][1] in plus_list:
              t_score += score
            if eval_list[i][1] in multiple_list:
              t_rein *= rein
            else:
              pass

      else:    
        word1 =  eval_dic_komoran.loc[(eval_dic_komoran['word'] == eval_list[idx][0]) & (eval_dic_komoran['tag'] == eval_list[idx][1])]  # '않' 평가 점수 데이터프레임
        word2 =  eval_dic_komoran.loc[(eval_dic_komoran['word'] == eval_list[idx-1][0]) & (eval_dic_komoran['tag'] == eval_list[idx-1][1])] # '않' 앞의 평가어휘의 점수 데이터프레임

        weight = float(word1['reinforcer'].unique())#않
        score = float(word2['score'].unique())

        neg_disig_score = weight * score

        # 2-1. 나머지 어휘들의 점수 계산과 합산
        del eval_list[idx-1:idx+1]  # '않'과 '않'과 결합한 평가 어휘를 리스트에서 제거

        for i in range(len(eval_list)):
          temp = eval_dic_komoran.loc[(eval_dic_komoran['word'] == eval_list[i][0]) & (eval_dic_komoran['tag'] == eval_list[i][1])]
          if temp.empty != True:
            score = float(temp['score'].unique())  #않
            rein = float(temp['reinforcer'].unique())

            word = list(temp.word)[0]

            if eval_list[i][1] in plus_list:
              t_score += score
            if eval_list[i][1] in multiple_list:
              t_rein *= rein
            else:
              pass

    ### '안' + '평가어휘' ###        
    elif ('안', 'MAG') in eval_list:
      idx = eval_list.index(('안', 'MAG'))

      if (len(eval_list)-1) == idx:
        del eval_list[idx:idx+2]  

        for i in range(len(eval_list)):
          temp = eval_dic_komoran.loc[(eval_dic_komoran['word'] == eval_list[i][0]) & (eval_dic_komoran['tag'] == eval_list[i][1])]
          if temp.empty != True:
            score = float(temp['score'].unique())  #안
            rein = float(temp['reinforcer'].unique())

            word = list(temp.word)[0]

            if eval_list[i][1] in plus_list:
              t_score += score
            if eval_list[i][1] in multiple_list:
              t_rein *= rein
            else:
              pass 
      

      else:
        word1 =  eval_dic_komoran.loc[(eval_dic_komoran['word'] == eval_list[idx][0]) & (eval_dic_komoran['tag'] == eval_list[idx][1])]  # '안' 평가 점수 데이터프레임
        word2 =  eval_dic_komoran.loc[(eval_dic_komoran['word'] == eval_list[idx+1][0]) & (eval_dic_komoran['tag'] == eval_list[idx+1][1])] # '안' 뒤에 따라오는 평가어휘의 점수 데이터프레임      

        weight = float(word1['reinforcer'].unique())#안
        score = float(word2['score'].unique())

        neg_disig_score = weight * score

        # 2-1. 나머지 어휘들의 점수 계산과 합산
        del eval_list[idx:idx+2]  # '않'과 '않'과 결합한 평가 어휘를 리스트에서 제거

        for i in range(len(eval_list)):
          temp = eval_dic_komoran.loc[(eval_dic_komoran['word'] == eval_list[i][0]) & (eval_dic_komoran['tag'] == eval_list[i][1])]
          if temp.empty != True:
            score = float(temp['score'].unique())  #안
            rein = float(temp['reinforcer'].unique())

            word = list(temp.word)[0]

            if eval_list[i][1] in plus_list:
              t_score += score
            if eval_list[i][1] in multiple_list:
              t_rein *= rein
            else:
              pass

    ### '못' + '평가어휘' ###        
    elif ('못', 'MAG') in eval_list:
      idx = eval_list.index(('못', 'MAG'))

      if idx == (len(eval_list)-1):
        del eval_list[idx]  # '못'제거

        for i in range(len(eval_list)):
          temp = eval_dic_komoran.loc[(eval_dic_komoran['word'] == eval_list[i][0]) & (eval_dic_komoran['tag'] == eval_list[i][1])]
          if temp.empty != True:
            score = float(temp['score'].unique()) 
            rein = float(temp['reinforcer'].unique())

            word = list(temp.word)[0]

            if eval_list[i][1] in plus_list:
              t_score += score
            if eval_list[i][1] in multiple_list:
              t_rein *= rein
            else:
              pass
      
      else:
        word1 =  eval_dic_komoran.loc[(eval_dic_komoran['word'] == eval_list[idx][0]) & (eval_dic_komoran['tag'] == eval_list[idx][1])]  # 
        word2 =  eval_dic_komoran.loc[(eval_dic_komoran['word'] == eval_list[idx+1][0]) & (eval_dic_komoran['tag'] == eval_list[idx+1][1])] # 

        weight = float(word1['reinforcer'].unique()) # 못
        score = float(word2['score'].unique())

        neg_disig_score = weight * score

      # 2-1. 나머지 어휘들의 점수 계산과 합산
      del eval_list[idx:idx+2]  # '못'과 '못'과 결합한 평가 어휘를 리스트에서 제거

      for i in range(len(eval_list)):
        temp = eval_dic_komoran.loc[(eval_dic_komoran['word'] == eval_list[i][0]) & (eval_dic_komoran['tag'] == eval_list[i][1])]
        if temp.empty != True:
          score = float(temp['score'].unique()) # 못
          rein = float(temp['reinforcer'].unique())

          word = list(temp.word)[0]

          if eval_list[i][1] in plus_list:
            t_score += score
          if eval_list[i][1] in multiple_list:
            t_rein *= rein
          else:
            pass

    ### '평가어휘' + '아니'
    elif ('아니', 'VCN') in eval_list:
      idx = eval_list.index(('아니', 'VCN'))

      if idx == 0:
        del eval_list[idx]  

        for i in range(len(eval_list)):
          temp = eval_dic_komoran.loc[(eval_dic_komoran['word'] == eval_list[i][0]) & (eval_dic_komoran['tag'] == eval_list[i][1])]
          if temp.empty != True:
            score = float(temp['score'].unique()) #아니
            rein = float(temp['reinforcer'].unique())

            word = list(temp.word)[0]

            if eval_list[i][1] in plus_list:
              t_score += score
            if eval_list[i][1] in multiple_list:
              t_rein *= rein
            else:
              pass

      else:
        word1 =  eval_dic_komoran.loc[(eval_dic_komoran['word'] == eval_list[idx][0]) & (eval_dic_komoran['tag'] == eval_list[idx][1])]  # '아니' 평가 점수 데이터프레임
        word2 =  eval_dic_komoran.loc[(eval_dic_komoran['word'] == eval_list[idx-1][0]) & (eval_dic_komoran['tag'] == eval_list[idx-1][1])] # '아니' 앞의 평가어휘의 점수 데이터프레임

        weight = float(word1['reinforcer'].unique()) #아니
        score = float(word2['score'].unique())

        neg_disig_score = weight * score

        # 2-1. 나머지 어휘들의 점수 계산과 합산
        del eval_list[idx-1:idx+1]  # '않'과 '않'과 결합한 평가 어휘를 리스트에서 제거

        for i in range(len(eval_list)):
          temp = eval_dic_komoran.loc[(eval_dic_komoran['word'] == eval_list[i][0]) & (eval_dic_komoran['tag'] == eval_list[i][1])]
          if temp.empty != True:
            score = float(temp['score'].unique()) #아니
            rein = float(temp['reinforcer'].unique())

            word = list(temp.word)[0]

            if eval_list[i][1] in plus_list:
              t_score += score
            if eval_list[i][1] in multiple_list:
              t_rein *= rein
            else:
               pass
            
    else:
      for i in range(len(eval_list)):
        temp = eval_dic_komoran.loc[(eval_dic_komoran['word'] == eval_list[i][0]) & (eval_dic_komoran['tag'] == eval_list[i][1])]
        if temp.empty != True:
          score = float(temp['score'].unique()) #그냥
          rein = float(temp['reinforcer'].unique())

          word = list(temp.word)[0]

          if eval_list[i][1] in plus_list:
            t_score += score
          if eval_list[i][1] in multiple_list:
            t_rein *= rein
          else:
            pass
    if t_rein == 0:
      t_rein = 1
    else:
      pass

    score = (t_score * t_rein) + neg_disig_score
    return score

# 사운드 점수 계산
from konlpy.tag import Komoran

# 사운드 사용자 사전 추가 적용
komoran = Komoran(userdic='/content/drive/MyDrive/6조_자연어처리 프로젝트/평가어휘 사전/사운드/user_dict_sound.txt')


eval_dic_komoran = pd.DataFrame(columns=['word', 'tag', 'reinforcer', 'score'])
file = pd.read_csv('/content/drive/MyDrive/6조_자연어처리 프로젝트/평가어휘 사전/사운드/score_dict_sound.txt')

eval_dic_komoran['word'] = file.word
eval_dic_komoran['tag'] = file.tag
eval_dic_komoran['reinforcer'] = file.reinforcer
eval_dic_komoran['score'] = file.score

def sound_translate(text):
  text = text.replace("ㅈㄴ", "너무")
  text = text.replace("존내", "너무")
  text = text.replace("넘모", "너무")
  text = text.replace("있었다면", "아쉽다")
  text = text.replace("들을 만", "괜찮다")
  text = text.replace("허접", "거슬리다")
  text = text.replace("끝장 나는", "멋지다")
  text = text.replace("뭣 같은","허접한")
  text = text.replace("갓", "멋지다")
  text = text.replace("리듬타게", "충만한")
  text = text.replace("울컥", "수려한")
  text = text.replace("듣고 싶은", "적절한")
  text = text.replace("수밖에 없", " ")
  text = text.replace("말이 필요없다", "멋지다")
  text = text.replace("좋아서", "좋다")
  text = text.replace("걸맞", "알맞는")
  text = text.replace("수가 없", " ")
  text = text.replace("미칠거 같", "거슬리다")
  return text

sound_final_score = 0

for i in range(len(df_sound)):
  text = df_sound['리뷰'][i]
  text = sound_translate(text)

  a = Score(text)
  b = a.get_score()

  sound_final_score += b

print(sound_final_score)

# 유저 서비스 점수 계산
# 유저서비스 사전 추가 적용
komoran = Komoran(userdic='/content/drive/MyDrive/6조_자연어처리 프로젝트/평가어휘 사전/사운드/user_dict_sound.txt')


eval_dic_komoran = pd.DataFrame(columns=['word', 'tag', 'reinforcer', 'score'])
file = pd.read_csv('/content/drive/MyDrive/6조_자연어처리 프로젝트/평가어휘 사전/유저 서비스/score_dict_userservicet.txt')

eval_dic_komoran['word'] = file.word
eval_dic_komoran['tag'] = file.tag
eval_dic_komoran['reinforcer'] = file.reinforcer
eval_dic_komoran['score'] = file.score

def userservice_translate(text):
  text = text.replace("ㅈㄴ", "너무")
  text = text.replace("존내", "너무")
  text = text.replace("넘모", "너무")
  text = text.replace("깨작", "별로")
  text = text.replace("렉", "버그")
  text = text.replace("마음에 들", "추천 ")
  text = text.replace("버그", "심각한")
  text = text.replace("할수가없", "")
  text = text.replace("할 수가없", "")
  text = text.replace("좋같네", "좆")
  text = text.replace("오류", "심각한 ")
  text = text.replace("환불가능", "별로 ")
  text = text.replace("핵앤슬래시"," ")
  text = text.replace("핵앤 슬래시"," ")
  text = text.replace("발적화", "심각한 ")
  text = text.replace("해줄때도", "별로 ")
  text = text.replace("팅김", "심각한 ")
  text = text.replace("강제종료", "심각한 ")
  text = text.replace("강재종료", "심각한 " )
  text = text.replace("지침", "별로 ")
  text = text.replace("드랍", "심각한 ")
  text = text.replace("화면 밀림", "심각한 ")
  text = text.replace("화면밀림", "심각한 ")
  text = text.replace("개보다 못한", "심각한 ")
  text = text.replace("개보다못한", "심각한 ")
  text = text.replace("개 보다 못한", "심각한 ")
  text = text.replace("검은화면", "심각한 ")
  text = text.replace("개같음", "별로 ")
  text = text.replace("개x같음", "별로 ")
  text = text.replace("ㅈ", "별로 ")
  text = text.replace("랙", "심각한")
  text = text.replace("팅기고", "심각한")
  text = text.replace("좃", "좆 ")
  text = text.replace("해주세요", "얄밉다 ")
  text = text.replace("불가능", "심각한 ")
  text = text.replace("비추", "어려움")
  text = text.replace("기가차다", "심각한 ")
  text = text.replace("기가찬다", "심각한 ")
  text = text.replace("망겜", " 심각한 ")
  text = text.replace("한세월", "얄밉다 ")
  text = text.replace("있었으면 좋겠다", " 언짢다 ")
  text = text.replace("있었으면", " 언짢다 ")
  text = text.replace("초기화", "언짢다 ")
  text = text.replace("노답", "심각한 ")
  text = text.replace("병맛", "어려움 ")
  text = text.replace("목빠지게", "언짢다 ")
  text = text.replace("손 놓", "심각한 ")

  return text

userservice_final_score = 0

for i in range(len(df_us)):
  text = df_us['리뷰'][i]
  text = sound_translate(text)

  a = Score(text)
  b = a.get_score()
  userservice_final_score += b

print(userservice_final_score)

# 플레이 점수 계산
# 플레이 사전 추가 적용
komoran = Komoran(userdic='/content/drive/MyDrive/6조_자연어처리 프로젝트/평가어휘 사전/플레이/user_dict_play.txt')


eval_dic_komoran = pd.DataFrame(columns=['word', 'tag', 'reinforcer', 'score'])
file = pd.read_csv('/content/drive/MyDrive/6조_자연어처리 프로젝트/평가어휘 사전/플레이/score_dict_play.txt')

eval_dic_komoran['word'] = file.word
eval_dic_komoran['tag'] = file.tag
eval_dic_komoran['reinforcer'] = file.reinforcer
eval_dic_komoran['score'] = file.score

def play_translate(text):
  text = text.replace("ㅈㄴ", "너무")
  text = text.replace("존내", "너무")
  text = text.replace("넘모", "너무")
  text = text.replace("맹맹하", "비효율 ")
  text = text.replace("맹맹합", "비효율 ")
  text = text.replace("비효율", "짧다 ")
  text = text.replace("마음에 들", "치밀한")
  text = text.replace("개같", "꺾이다 ")
  text = text.replace("꺾이", "끄다 ")
  text = text.replace("길어지", "허무한")
  text = text.replace("시간가" , "귀엽다 ")
  text = text.replace("목표의식", "독창적인 ")
  text = text.replace("아닐까", "")
  text = text.replace("뻘짓", "짧다 ")
  text = text.replace("일원적", "짧다 ")
  text = text.replace("따봉", "엄청난 ")
  text = text.replace("비추", "끄다 ")
  text = text.replace("손절", "끄다 ")
  text = text.replace("시간소모", "끄다 ")
  text = text.replace("빡치게", "끄다")
  text = text.replace("좆같", "끄다 ")
  text = text.replace("마이너스", "끄다 ")
  text = text.replace("괴작", "끄다 ")
  text = text.replace("아니라", "")
  text = text.replace("졸", "짧다 ")
  text = text.replace("찝찝하게", "짧다 ")
 
  return text

play_final_score = 0

for i in range(len(df_play)):
  text = df_play['리뷰'][i]
  text = play_translate(text)

  a = Score(text)
  b = a.get_score()
  play_final_score += b

print(play_final_score)

# 난이도 점수 계산
# 난이도 사전 추가 적용
komoran = Komoran(userdic='/content/drive/MyDrive/6조_자연어처리 프로젝트/평가어휘 사전/난이도/user_dict_level.txt')


eval_dic_komoran = pd.DataFrame(columns=['word', 'tag', 'reinforcer', 'score'])
file = pd.read_csv('/content/drive/MyDrive/6조_자연어처리 프로젝트/평가어휘 사전/난이도/score_dict_level.txt')

eval_dic_komoran['word'] = file.word
eval_dic_komoran['tag'] = file.tag
eval_dic_komoran['reinforcer'] = file.reinforcer
eval_dic_komoran['score'] = file.score

def level_translate(text):
  text = text.replace("ㅈㄴ", "너무")
  text = text.replace("존내", "너무")
  text = text.replace("넘모", "너무")
  text = text.replace("난이도 있음", "필요")
  text = text.replace("환불 가능", "호구")
  text = text.replace("도전정신", "상승")
  text = text.replace("도전 정신", "상승")
  text = text.replace("빡세", "환불")
  text = text.replace("헬", "환불")
  text = text.replace("하라고", "필요")
  text = text.replace("운빨", "까다롭다")
  text = text.replace("운 빨", "까다롭다")
  text = text.replace("고난이도", "스트레스")
  text = text.replace("호구", "힐링")
  text = text.replace("혈압", "하드코어")
  text = text.replace("스트레스", "살벌한")
  text = text.replace("무자비", "살벌한")
  text = text.replace("불친절", "극악")
 
  return text

level_final_score = 0

for i in range(len(df_level)):
  text = df_level['리뷰'][i]
  text = level_translate(text)

  a = Score(text)
  b = a.get_score()
  level_final_score += b

print(level_final_score)

# 그래픽 점수 계산
# 플레이 사전 추가 적용
komoran = Komoran(userdic='/content/drive/MyDrive/6조_자연어처리 프로젝트/평가어휘 사전/그래픽/user_dict_graphic.txt')


eval_dic_komoran = pd.DataFrame(columns=['word', 'tag', 'reinforcer', 'score'])
file = pd.read_csv('/content/drive/MyDrive/6조_자연어처리 프로젝트/평가어휘 사전/그래픽/score_dict_graphic.txt')

eval_dic_komoran['word'] = file.word
eval_dic_komoran['tag'] = file.tag
eval_dic_komoran['reinforcer'] = file.reinforcer
eval_dic_komoran['score'] = file.score

def graphic_translate(text):
  text = text.replace("ㅈㄴ", "너무")
  text = text.replace("존내", "너무")
  text = text.replace("넘모", "너무")
  text = text.replace("맘", "마음")
  text = text.replace("었던", " ")
  text = text.replace("었"," ")
  text = text.replace("마음에 들", "황홀한 ")
  text = text.replace("정성이 들", "만족도 ")
  text = text.replace("과해", "혼잡 ")
  text = text.replace("과해", "혼잡 ")
  text = text.replace("잘 갖춰", "완벽한 ")
  text = text.replace("잘 갖추", "완벽한 ")
  text = text.replace("내다 버리", "불합리 ")
  text = text.replace("내다 버렸", "불합리 ")
  text = text.replace("매력", "참신한 ")
  text = text.replace("정교", "참신한 ")
  text = text.replace("질리", "어설프다 ")
  text = text.replace("질린", "어설프다 ")
  text = text.replace("잘 뽑", "진수 ")
  text = text.replace("매끄러", "섬세한 ")
  text = text.replace("매끄럽", "섬세한 ")
  text = text.replace("오짐", "만족한 ")
  text = text.replace("신박", "세련된 ")
  text = text.replace("지림", "진수 ")
  text = text.replace("지린", "진수 ")
  text = text.replace("다채", "친절한 ")
  text = text.replace("좇", "좆 ")
  text = text.replace("좆같", "지랄 ")
  text = text.replace("병신", "지랄 ")
  text = text.replace("답도 없는", "답 없는")
  text = text.replace("씨발", "지랄")
  text = text.replace("못한", "흑우 ")
  text = text.replace("흑우", "떨어지다 ")
  text = text.replace("텐데", "망설이다 ")
  text = text.replace("지직", "망설이다 ")
  text = text.replace("낮", "떨어지다 ")
  text = text.replace("퇴화", "떨어지다 ")
  text = text.replace("극혐", "떨어지다 ")
  text = text.replace("세세", "어우러지다 ")
  text = text.replace("신기", "어우러지다 ")
  text = text.replace("부자연", "망설이다 ")
  text = text.replace("불편", "떨어지다 ")
  text = text.replace("리얼", "어우러지다 ")
  text = text.replace("준수", "어우러지다 ")
  text = text.replace("볼일 없", "망설이다 ")
  text = text.replace("무성의", "망설이다 ")
  text = text.replace("걸맞는", "어우러지다 ")
  text = text.replace("아까", "망설이다 ")
  text = text.replace("아깝", "망설이다 ")
  text = text.replace("빻", " 떨어지다 ")
  text = text.replace("고퀄", "진수 ")
  text = text.replace("저사양", "어우러지다 ")
 
  return text

graphic_final_score = 0

for i in range(len(df_graphic)):
  text = df_graphic['리뷰'][i]
  text = graphic_translate(text)

  a = Score(text)
  b = a.get_score()
  graphic_final_score += b

print(graphic_final_score)

# 스토리 점수 계산
# 스토리 사전 추가 적용
komoran = Komoran(userdic='/content/drive/MyDrive/6조_자연어처리 프로젝트/평가어휘 사전/스토리/user_dict_story.txt')


eval_dic_komoran = pd.DataFrame(columns=['word', 'tag', 'reinforcer', 'score'])
file = pd.read_csv('/content/drive/MyDrive/6조_자연어처리 프로젝트/평가어휘 사전/스토리/score_dict_story.txt')

eval_dic_komoran['word'] = file.word
eval_dic_komoran['tag'] = file.tag
eval_dic_komoran['reinforcer'] = file.reinforcer
eval_dic_komoran['score'] = file.score

def story_translate(text): 
  text = text.replace("녹아" , "재미있다 ")
  text = text.replace("어이가 없", "어이없다")
  text = text.replace("비추천", "스킵 ")
  text = text.replace("중요", "참신한 ")
  text = text.replace("강제", "최악 ")
  text = text.replace("짱", "띵작 ")
  return text

story_final_score = 0

for i in range(len(df_story)):
  text = df_story['리뷰'][i]
  text = story_translate(text)

  a = Score(text)
  b = a.get_score()
  story_final_score += b

print(story_final_score)

# 정량화 시각화
df_score = pd.DataFrame(columns=['사운드','유저 서비스', '플레이', '스토리','난이도','그래픽'])

new_data = {'사운드':sound_final_score,
            '유저 서비스':userservice_final_score,
            '플레이': play_final_score,
            '스토리':story_final_score,
            '난이도':level_final_score,
            '그래픽':graphic_final_score}

df_score = df_score.append(new_data, ignore_index=True)
df_score = df_score.T
df_score = df_score.rename(columns={0:'지표'})

from matplotlib import pyplot as plt

df_score.plot(kind='barh')