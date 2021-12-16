# -*- coding: utf-8 -*-
"""
점수 계산 프로세스
"""
# 코랩 환경에서 konlpy 설치
!set -x \
&& pip install konlpy \
&& curl -s https://raw.githubusercontent.com/konlpy/konlpy/master/scripts/mecab.sh | bash -x

#%%
# 필요한 라이브러리 설치 및 드라이브 마운트
import pandas as pd
import numpy as np
pd.set_option('display.max_colwidth', -1)

from google.colab import drive
drive.mount('/content/drive')

from konlpy.tag import Komoran
#%%

# 사운드 사용자 사전 추가 적용
komoran = Komoran(userdic='/content/drive/MyDrive/6조_자연어처리 프로젝트/평가어휘 사전/사운드/user_dict_sound.txt')

# 평가 어휘 사전 로드
eval_dic_komoran = pd.DataFrame(columns=['word','tag', 'reinforcer', 'score'])
file = pd.read_csv('/content/drive/MyDrive/6조_자연어처리 프로젝트/평가어휘 사전/사운드/score_dict_sound.txt')

eval_dic_komoran['word'] = file.word
eval_dic_komoran['tag'] = file.tag
eval_dic_komoran['reinforcer'] = file.reinforcer
eval_dic_komoran['score'] = file.score
#%%
# 점수 계산 class
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
#%%
# user dictionary가 적용되지 않는 경우 같은 점수의 단어로 치환하는 함수
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
#%%
# 점수 계산 테스트
text = '귀가 예민하신분들은 음악들으실때 노이즈가 들리실겁니다.'

text = sound_translate(text)

a = Score(text)
b = a.get_score()

print(b)