# -*- coding: utf-8 -*-
"""

전처리 프로세스 코드

"""
!pip install soynlp
!pip install kss
!pip install git+https://github.com/ssut/py-hanspell.git
#%%
import re

# 이모티콘 제거
emoji_pattern = re.compile("["
        u"\U0001F600-\U0001F64F"  # emoticons
        u"\U0001F300-\U0001F5FF"  # symbols & pictographs
        u"\U0001F680-\U0001F6FF"  # transport & map symbols
        u"\U0001F1E0-\U0001F1FF"  # flags (iOS)
                           "]+", flags=re.UNICODE)
for i in range(len(df)):
    df['리뷰'][i] = emoji_pattern.sub(r'', df['리뷰'][i])


#%%

# 반복되는 문자 normalization
from soynlp.normalizer import *

for i in range(len(df)):
  df['리뷰'][i] = repeat_normalize(df['리뷰'][i], num_repeats=3)

#%%

# 맞춤법 검사
from hanspell import spell_checker

spell_checked_review = list()
for idx in range(len(df)): # 우선 20개만 테스트
  if '☐' in spacing_review[idx]:  #☐문자가 있으면 오류가 나므로 건너뜀
    spell_checked_review.append(spacing_review[idx])
  else:
    df['리뷰'][idx] = spell_checker.check(df['리뷰'][idx])

#%%

# 토큰화
from konlpy.tag import Komoran
tagger = Komoran()

df['토큰'] = 0

for i in range(len(df)):
  df['토큰'][i] = tagger.morphs(df['리뷰'][i])

#%%
stop_words = ['이','을','에','가','를','도','의','들','은','라며','는','하고','로', '수', '것', '!', '...', '..','하는', '!!', '할', '으로', '다', '에서', '☐', '만', '때', '입니다','하면' ]

for i in range(len(df)):
  clean_words = []
  for w in df['토큰'][i]:
    if w not in stop_words:
      clean_words.append(w)
  df['전처리 상태'][i] = clean_words
  

#%%
# 속성어 개념 유사어 추출

tokenized_data = []

for sentence in df['리뷰']:
    temp_X = tagger.nouns(sentence) # 토큰화
    temp_X = [word for word in temp_X if not word in stop_words] # 불용어 제거
    tokenized_data.append(temp_X)


from gensim.models import Word2Vec

model = Word2Vec(sentences = tokenized_data, size = 100, window = 5, min_count = 5, workers = 4, sg = 0)

# 속성 개념 유사어 리스트 생성

###그래픽
graphic = []
for i in range(150):
  graphic.append(model.wv.most_similar('그래픽', topn=150)[i][0])

###플레이
play = []
for i in range(150):
  play.append(model.wv.most_similar('플레이', topn=150)[i][0])

###사운드
sound = []
for i in range(150):
  sound.append(model.wv.most_similar('사운드', topn=150)[i][0])

###난이도
level = []
for i in range(150):
  level.append(model.wv.most_similar('난이도', topn=150)[i][0])

###스토리
story = []
for i in range(150):
  story.append(model.wv.most_similar('스토리', topn=150)[i][0])

###버그
bug = []
for i in range(150):
  bug.append(model.wv.most_similar('버그', topn=150)[i][0])

# 텍스트 파일로 저장
with open('그래픽_유사속성어.txt', 'w', encoding='UTF-8') as f:
  for w in graphic:
    f.write(w+'\n')
with open('플레이_유사속성어.txt', 'w', encoding='UTF-8') as f:
  for w in play:
    f.write(w+'\n')
with open('사운드_유사속성어.txt', 'w', encoding='UTF-8') as f:
  for w in sound:
    f.write(w+'\n')
with open('난이도_유사속성어.txt', 'w', encoding='UTF-8') as f:
  for w in level:
    f.write(w+'\n')
with open('스토리_유사속성어.txt', 'w', encoding='UTF-8') as f:
  for w in story:
    f.write(w+'\n')
with open('버그_유사속성어.txt', 'w', encoding='UTF-8') as f:
  for w in bug:
    f.write(w+'\n')