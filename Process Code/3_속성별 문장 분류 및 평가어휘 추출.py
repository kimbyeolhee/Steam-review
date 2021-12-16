# -*- coding: utf-8 -*-
"""

평가어휘 사전 구축

"""

#%%
!set -x \
&& pip install konlpy \
&& curl -s https://raw.githubusercontent.com/konlpy/konlpy/master/scripts/mecab.sh | bash -x

import pandas as pd
from konlpy.tag import Komoran

#%% 
# 속성어 사전 로드

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

#%%
# 리뷰 데이터 로드
review_url = 'https://raw.githubusercontent.com/kimbyeolhee/Steam-review/main/prototype/prototype_review.txt'
raw_df = pd.read_csv(review_url, sep='\t')

df= pd.DataFrame(raw_df[['리뷰','label']])

# nan값 제거
df = df.dropna(axis=0, how='any')
df = df.drop_duplicates()
df = df.reset_index(drop=True)

#%% 전처리 과정
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

from hanspell import spell_checker

spell_checked_review = list()
for idx in range(len(spacing_review)): 
  if '☐' in spacing_review[idx]:
    spell_checked_review.append(spacing_review[idx])
  else:
    spelled_sent = spell_checker.check(spacing_review[idx])
    checked_sent = spelled_sent.checked
    spell_checked_review.append(checked_sent)
    
from soynlp.normalizer import *

normalized_review = list()
for idx in range(len(df)): 
  normalized_review.append(repeat_normalize(df['리뷰'][idx], num_repeats=2))

import kss

sentence_tokenized_review = []
for idx in range(len(normalized_review)): 
  if '☐' in normalized_review[idx]:
    sentence_tokenized_review.append(normalized_review[idx])
  else:
    for sent in kss.split_sentences(normalized_review[idx]):
        sentence_tokenized_review.append(sent.strip())
        
#%%
# 속성 별 문장 분류   
df_attr_class = pd.DataFrame(columns=['리뷰','사운드','유저서비스','난이도','그래픽','플레이','스토리'])

# 전처리된 리뷰 리스트
review_sents = sentence_tokenized_review  

for idx, sent in enumerate(review_sents):
  # 속성어 갯수 카운트
  sound_count, US_count, level_count, graphic_count, play_count, story_count = 0, 0, 0, 0, 0, 0

  # 리뷰에서 속성어 확인
  for attr in list_sound:
    sound_count += sent.count(attr)
  for attr in list_US:
    US_count += sent.count(attr)
  for attr in list_level:
    level_count += sent.count(attr)
  for attr in list_graphic:
    graphic_count += sent.count(attr)
  for attr in list_play:
    play_count += sent.count(attr)
  for attr in list_story:
    story_count += sent.count(attr)

  # 결과 데이터프레임에 추가
  df_attr_class.loc[idx] = [sent,sound_count, US_count, level_count, graphic_count, play_count, story_count]

#%%
# 속성 문장 리스트
sound_review = list()
US_review = list()
level_review = list()
graphic_review = list()
play_review = list()
story_review = list()

for idx in range(len(df_attr_class)):
  sound = df_attr_class['사운드'][idx]
  US = df_attr_class['유저서비스'][idx]
  level = df_attr_class['난이도'][idx]
  graphic = df_attr_class['그래픽'][idx]
  play = df_attr_class['플레이'][idx]
  story = df_attr_class['스토리'][idx]

  nst = [['사운드', sound], ['유저서비스', US], ['난이도',level], ['그래픽',graphic], ['플레이',play], ['스토리',story]]
  col_name, max_value = max(nst, key=lambda item: item[1])

  if (sound == 0) & (US == 0) & (level == 0) & (graphic == 0) & (play == 0) &(story == 0): #모두 0값인 것은 제외
    pass

  else:
    if col_name == '사운드':
      sound_review.append(df_attr_class['리뷰'][idx])
    elif col_name =='유저서비스':
      US_review.append(df_attr_class['리뷰'][idx])
    elif col_name == '난이도':
      level_review.append(df_attr_class['리뷰'][idx])
    elif col_name == '그래픽':
      graphic_review.append(df_attr_class['리뷰'][idx])
    elif col_name == '플레이':
      play_review.append(df_attr_class['리뷰'][idx])
    elif col_name == '스토리':
      story_review.append(df_attr_class['리뷰'][idx])
     
#%%
# 빈출 어휘 추출
from konlpy.tag import Komoran
komoran = Komoran()

# 타겟 형태소
target_tags = ['NNG','VV','VA','MAG','XR','NNP','NNB']

### 사운드
df_sound_pos = pd.DataFrame(columns=['리뷰','형태소','target'])

for idx, sent in enumerate(sound_review):
  if '\U0001f7e9' in sent:
    pass

  else:
    temp = []
    for pos in komoran.pos(sent):
      if pos[1] in target_tags:
        temp.append(pos)
    df_sound_pos.loc[idx] = [sent, komoran.pos(sent), temp]

import itertools
from collections import Counter

count_tokens = list(itertools.chain.from_iterable(df_sound_pos['target']))
Counter(count_tokens).most_common()[:500]


### 유저서비스
df_US_pos = pd.DataFrame(columns=['리뷰','형태소','target'])

for idx, sent in enumerate(US_review):
  if '\U0001f7e9' in sent:
    pass

  else:
    temp = []
    for pos in komoran.pos(sent):
      if pos[1] in target_tags:
        temp.append(pos)
    df_US_pos.loc[idx] = [sent, komoran.pos(sent), temp]

count_tokens = list(itertools.chain.from_iterable(df_US_pos['target']))
Counter(count_tokens).most_common()[:500]

### 난이도
df_level_pos = pd.DataFrame(columns=['리뷰','형태소','target'])

for idx, sent in enumerate(level_review):
  if '\U0001f7e9' in sent:
    pass

  else:
    temp = []
    for pos in komoran.pos(sent):
      if pos[1] in target_tags:
        temp.append(pos)
    df_level_pos.loc[idx] = [sent, komoran.pos(sent), temp]

### 그래픽
df_graphic_pos = pd.DataFrame(columns=['리뷰','형태소','target'])

for idx, sent in enumerate(graphic_review):
  if '\U0001f7e9' in sent:
    pass

  else:
    temp = []
    for pos in komoran.pos(sent):
      if pos[1] in target_tags:
        temp.append(pos)
    df_graphic_pos.loc[idx] = [sent, komoran.pos(sent), temp]

count_tokens = list(itertools.chain.from_iterable(df_graphic_pos['target']))
Counter(count_tokens).most_common()[:500]

### 플레이
df_play_pos = pd.DataFrame(columns=['리뷰','형태소','target'])

for idx, sent in enumerate(play_review):
  if '\U0001f7e9' in sent:
    pass

  else:
    temp = []
    for pos in komoran.pos(sent):
      if pos[1] in target_tags:
        temp.append(pos)
    df_play_pos.loc[idx] = [sent, komoran.pos(sent), temp]

count_tokens = list(itertools.chain.from_iterable(df_play_pos['target']))
Counter(count_tokens).most_common()[:500]

### 스토리
df_story_pos = pd.DataFrame(columns=['리뷰','형태소','target'])

for idx, sent in enumerate(story_review):
  if '\U0001f7e9' in sent:
    pass

  else:
    temp = []
    for pos in komoran.pos(sent):
      if pos[1] in target_tags:
        temp.append(pos)
    df_story_pos.loc[idx] = [sent, komoran.pos(sent), temp]
    
count_tokens = list(itertools.chain.from_iterable(df_story_pos['target']))
Counter(count_tokens).most_common()[:500]
