import time
def get_putable_spaces(board,hand):
  putable_spaces=[]
  num_space=0
  for i in range(8):
    for j in range(8):
      if board[i][j]!=-1:continue
      num_space+=1
      flg=False
      for di in (0,1,-1):
        for dj in (0,1,-1):
          if di==dj==0:continue
          if flg:break
          ni,nj=i+di,j+dj
          if 0<=ni<8 and 0<=nj<8:
            if board[ni][nj]!=-1 and board[ni][nj]!=hand:
              ni,nj=ni+di,nj+dj
              while 0<=ni<8 and 0<=nj<8 and board[ni][nj]!=-1 and board[ni][nj]!=hand:
                ni,nj=ni+di,nj+dj
              if 0<=ni<8 and 0<=nj<8 and board[ni][nj]!=-1 and board[ni][nj]==hand:
                flg=True
      if flg:putable_spaces.append([i,j])
  return putable_spaces,num_space

def get_board_if_put_piece(i,j,board,hand):
  if board[i][j]!=-1:return None
  board_copy=[x[:] for x in board]
  cnt=0
  for di in (0,1,-1):
    for dj in (0,1,-1):
      if di==dj==0:continue
      ni,nj=i+di,j+dj
      if 0<=ni<8 and 0<=nj<8:
        if board_copy[ni][nj]!=-1 and board_copy[ni][nj]!=hand:
          ni,nj=ni+di,nj+dj
          while 0<=ni<8 and 0<=nj<8 and board_copy[ni][nj]!=-1 and board_copy[ni][nj]!=hand:
            ni,nj=ni+di,nj+dj
          if 0<=ni<8 and 0<=nj<8 and board_copy[ni][nj]!=-1 and board_copy[ni][nj]==hand:
            ii,jj=i,j
            while [ii,jj]!=[ni,nj]:
              board_copy[ii][jj]=hand
              ii,jj=ii+di,jj+dj
              cnt+=1
  if cnt==0:return None
  board_copy[i][j]=hand
  return board_copy

class OthelloBoard():
  def __init__(self):
    self.board=[[-1]*8 for _ in range(8)]
    # -1:space 0:white 1:black
    self.board[3][3]=0
    self.board[4][4]=0
    self.board[4][3]=1
    self.board[3][4]=1
    # black is first
    self.hand=1
    self.spaces=get_putable_spaces(self.board,self.hand)[0]

  def put_piece(self,i,j):
    if [i,j] not in self.spaces:return None
    self.board[i][j]=self.hand
    hand=self.hand
    for di in (0,1,-1):
      for dj in (0,1,-1):
        if di==dj==0:continue
        ni,nj=i+di,j+dj
        if 0<=ni<8 and 0<=nj<8:
          if self.board[ni][nj]!=-1 and self.board[ni][nj]!=hand:
            ni,nj=ni+di,nj+dj
            while 0<=ni<8 and 0<=nj<8 and self.board[ni][nj]!=-1 and self.board[ni][nj]!=hand:
              ni,nj=ni+di,nj+dj
            if 0<=ni<8 and 0<=nj<8 and self.board[ni][nj]!=-1 and self.board[ni][nj]==hand:
              ii,jj=i,j
              while [ii,jj]!=[ni,nj]:
                self.board[ii][jj]=hand
                ii,jj=ii+di,jj+dj
    self.hand=self.hand^1
    self.spaces=get_putable_spaces(self.board,self.hand)[0]

  def pass_turn(self):
    self.hand=self.hand^1
    self.spaces=get_putable_spaces(self.board,self.hand)[0]
  
  def finish_game(self):
    num0,num1=0,0
    for i in range(8):
      for j in range(8):
        if self.board[i][j]==0:num0+=1
        if self.board[i][j]==1:num1+=1
    return num0,num1

weight=[]
weight.append([30,-12,0,-1,-1,0,-12,30])
weight.append([-12,-15,-3,-3,-3,-3,-15,-12])
weight.append([0,-3,0,-1,-1,0,-3,0])
weight.append([-1,-3,-1,-1,-1,-1,-3,-1])
weight.append([-1,-3,-1,-1,-1,-1,-3,-1])
weight.append([0,-3,0,-1,-1,0,-3,0])
weight.append([-12,-15,-3,-3,-3,-3,-15,-12])
weight.append([30,-12,0,-1,-1,0,-12,30])

# handから見た場面の評価値。序盤。端を取るほど評価高い。
def eval_board_first(board,hand):
  score0,score1=0,0
  spaces0=get_putable_spaces(board,hand)[0]
  spaces1=get_putable_spaces(board,hand^1)[0]
  for i in range(8):
    for j in range(8):
      if board[i][j]==hand:
        score0+=weight[i][j]
      if board[i][j]==hand^1:
        score1+=weight[i][j]
  k=1
  score0+=k*len(spaces0)
  score1+=k*len(spaces1)
  return score0-score1

# handから見た場面の評価値。終盤。駒数が多いほど評価高い。
def eval_board_second(board,hand):
  score0,score1=0,0
  for i in range(8):
    for j in range(8):
      if board[i][j]==hand:
        score0+=1
      if board[i][j]==hand^1:
        score1+=1
  return score0-score1

import sys
sys.setrecursionlimit(100)
def search_best_put_position(board,eval_function,deep_num,hand):
  """
  min-max法により、最適な置き場所を探す。
  :param board:オセロ盤
  :param eval_function:盤の評価関数
  :param deep_num:探索深さ。数が多いほど強い手を打つ。
  :param hand:どちらの手番かを示す。
  """
  def search(board,hand,num):
    """
    相手(hand^1)の評価値が最も低くなる場所に置く。
    """
    spaces,num_space=get_putable_spaces(board,hand)
    if len(spaces)==0:
      return eval_function(board,hand^1),(-1,-1)
    #assert len(spaces)==0 and num_space>0,'error'
      
    if num==deep_num:
      best_score=10**10
      best_position=[]
      for i,j in spaces:
        board_if=get_board_if_put_piece(i,j,board,hand)
        score=eval_function(board_if,hand^1)
        if score==best_score:
          best_position.append([i,j])
        elif score<best_score:
          best_position=[[i,j]]
          best_score=score
    elif (deep_num-num)%2==0:
      best_score=10**10
      best_position=[]
      for i,j in spaces:
        board_if=get_board_if_put_piece(i,j,board,hand)
        score,position=search(board_if,hand^1,num+1)
        if score==best_score:
          best_position.append([i,j])
        elif score<best_score:
          best_position=[[i,j]]
          best_score=score
    else:
      best_score=-10**10
      best_position=[]
      for i,j in spaces:
        board_if=get_board_if_put_piece(i,j,board,hand)
        score,position=search(board_if,hand^1,num+1)
        if score==best_score:
          best_position.append([i,j])
        elif score>best_score:
          best_position=[[i,j]]
          best_score=score

    return best_score,best_position[randint(0,len(best_position)-1)]
  best_score,position=search(board,hand,0)
  return position

from random  import randint
# consol: you vs cp
if __name__=='__main__':
  ob=OthelloBoard()
  flg=False
  cnt=0
  print('-'*25)
  for x in ob.board:
    print('',*[[' ○',' ●','  '][y] for y in x],'',sep='|')
    print('-'*25)

  while True:
    spaces=ob.spaces
    if not spaces:
      if flg:break
      flg=True
      print('pass')
      ob.pass_turn()
      continue
    flg=False
    if ob.hand==1:
      board_view=[]
      for x in ob.board:
        board_view.append([[' ○',' ●','  '][y] for y in x])
      for i,(j,k) in enumerate(spaces):
        board_view[j][k]=(' '+str(i+1))[-2:]
      print('your turn ●. please input number of put position.')
      print('-'*25)
      for x in board_view:
        print('',*x,'',sep='|')
        print('-'*25)
      i=int(input())
      while not 1<=i<=len(spaces):
        print('uncorrect input.please retry.')
        i=int(input())
      i,j=spaces[i-1]
    else:
      print("cp's turn ○.")
      if 64-cnt>=12:
        position=search_best_put_position(ob.board,eval_board_first,3,ob.hand)
      else:
        position=search_best_put_position(ob.board,eval_board_second,3,ob.hand)
      i,j=position
    ob.put_piece(i,j)
    cnt+=1
    print('-'*25)
    for x in ob.board:
      print('',*[[' ○',' ●','  '][y] for y in x],'',sep='|')
      print('-'*25)
  
  num0,num1=ob.finish_game()
  print(f'you:{num1} cp:{num0} num colt:{num0+num1}')



from random  import randint
if __name__=='__main__1':
  num_v=0
  num_try=20
  for _ in range(num_try):
    ob=OthelloBoard()
    cnt=0
    flg=True
    while True:
      spaces=ob.spaces
      if spaces:
        if ob.hand==0:
          if 64-cnt>=12:
            position=search_best_put_position(ob.board,eval_board_first,2,ob.hand)
          else:
            position=search_best_put_position(ob.board,eval_board_second,5,ob.hand)
          i,j=position
        else:
          position=search_best_put_position(ob.board,eval_board_first,0,ob.hand)
          i,j=position
        ob.put_piece(i,j)
        flg=True
        cnt+=1
      else:
        ob.pass_turn()
        if flg:
          flg=False
        else:
          break
    num0,num1=ob.finish_game()
    if num1<num0:num_v+=1
    print(f'black:{num1} white:{num0} num colt:{num0+num1}')
  print(num_v/num_try)

