#wip source:https://github.com/VincentAC-stack/CSCI570-FinalProject/blob/main/9451263998_5033799212_7197616609_efficient.py
import sys
from resource import *
import time
import psutil
import numpy as np

def process_memory():
    process = psutil.Process()
    memory_info = process.memory_info()
    memory_consumed = int(memory_info.rss/1024)
    return memory_consumed

# hardcoded penalty matrix
gap_penalty = 30
def mismatch_penalty(base1, base2):
    base = 'ACGT'
    i1 = base.find(base1)
    i2 = base.find(base2)
    penalty_matrix = [[0, 110, 48, 94],
                      [110, 0, 118, 48],
                      [48, 118, 0, 110],
                      [94, 48, 110, 0]]
    return penalty_matrix[i1][i2]


# read input from txt files
def parse_input():
    input_file = sys.argv[1]
    output_file = sys.argv[2]

    f = open(input_file, "r")
    input_strings = []
    num1 = []
    num2 = []
    is_second = True
    for line in f.readlines():
        line = line.strip()
        if not line.isnumeric():
            input_strings.append(line)
            if len(input_strings) == 2:
                is_second = False
        else:
            if is_second:
                num1.append(int(line))
            else:
                num2.append(int(line))
    f.close()

    # return a list of two generated strings
    i = 0
    s1 = input_strings[0]
    while i < len(num1):
        s1 = s1[0:num1[i]+1] + s1 + s1[num1[i]+1 :]
        i += 1

    i = 0
    s2 = input_strings[1]
    while i < len(num2):
        s2 = s2[0:num2[i]+1] + s2 + s2[num2[i]+1 :]
        i += 1
    return s1, s2, output_file

# start with an empty path
P = []

def forward(s1,s2):
    B = np.zeros((len(s1)+1, 2))
    for i in range(1,len(s1)+1):
        B[i][0]= i * gap_penalty
    for j in range(1,len(s2)+1):
        B[0][1]= j * gap_penalty
        for i in range(1,len(s1)+1):
            B[i][1] = min(B[i-1][0] + mismatch_penalty(s1[i-1], s2[j-1]),
                          B[i-1][1]+ gap_penalty,
                          B[i][0] + gap_penalty)
        for i in range(0,len(s1)+1):
            B[i][0] = B[i][1]
    return (B.T)[1]


def backward(s1,s2):
    B = np.zeros((len(s1)+1, 2))
    for i in range(1,len(s1)+1):
        B[len(s1)-i][1]=i*gap_penalty
    for j in range(len(s2)-1,-1,-1):
        B[len(s1)][0]=(len(s2)-j) * gap_penalty
        for i in range(len(s1)-1, -1, -1):
            B[i][0]=min(B[i+1][1] + mismatch_penalty(s1[i], s2[j]),
                        B[i+1][0]+ gap_penalty,
                       B[i][1] + gap_penalty)
                       
        for i in range(0,len(s1)+1):
            B[i][1] = B[i][0]
    return (B.T)[0]



def get_path(OPT,s1,s2,x_ori, y_ori):
    s1_length = len(s1)
    s2_length = len(s2)
    #save path
    i= s1_length
    j= s2_length
    path=[[0 for col in range(s2_length+1)] for row in range(s1_length+1)]
    path[i][j]=1
    path[0][0]=1
    while i!=0 or j!=0:
        if  OPT[i][j]==OPT[i-1][j]+gap_penalty:
            path[i-1][j]=1
            i=i-1
        elif  OPT[i][j]==OPT[i][j-1]+gap_penalty:
            path[i][j-1] = 1
            j=j-1
        else:
            path[i-1][j - 1] = 1
            i=i-1
            j=j-1
    # path=np.array(path)
    for x_index,x in enumerate(path):
        for y_index in range(len(path[0])):
            if x[y_index] == 1:
                P.append([x_index+x_ori , y_index+y_ori])

    return P

def Alignment(X,Y, x_index, y_index):
    B = np.zeros((len(X)+1, len(Y)+1))
    for i in range(1,len(X)+1):
        B[i][0]=i*gap_penalty
    for j in range(1,len(Y)+1):
        B[0][j]=j*gap_penalty
        for i in range(1,len(X)+1):
            B[i][j]=min(B[i-1][j-1] + mismatch_penalty(X[i-1], Y[j-1]),
                        B[i-1][j]+ gap_penalty,
                       B[i][j-1] + gap_penalty)
    get_path(B,X,Y,x_index,y_index)
    return 0


def perform_alignment_dc(s1, s2, s1_index, s2_index):
    s1_length = len(s1)
    s2_length = len(s2)
    if s1_length <= 2 or s2_length <= 2:
        Alignment(s1, s2, s1_index, s2_index)
    else:
        f = np.array(forward(s1, s2[0:s2_length//2]))
        g = np.array(backward(s1, s2[s2_length//2+1:s2_length]))
        sum_list = f + g
        min_sum = sum_list[0]
        min_index = 0
        for index, one in enumerate(sum_list):
            if one < min_sum:
                min_sum = one
                min_index = index
        P.append([min_index + s1_index, s2_length//2 + s2_index])
        perform_alignment_dc(s1[0:min_index], s2[0:s2_length//2], s1_index, s2_index)
        perform_alignment_dc(s1[min_index:s1_length], s2[s2_length//2:s2_length], min_index + s1_index, s2_length//2 + s2_index)
    return P

def get_string_DC(P,s1,s2):
    index = 0
    s1_aligned = ''
    s2_aligned = ''
    i = 0
    j = 0
    while index < len(P)-1:
        if P[index][0]<P[index+1][0] and P[index][1]==P[index+1][1] :
            s1_aligned = s1_aligned + s1[i]
            s2_aligned = s2_aligned + '_'
            i = i + 1
        elif P[index][0]==P[index+1][0] and P[index][1]<P[index+1][1] :
            s1_aligned = s1_aligned + '_'
            s2_aligned = s2_aligned + s2[j]
            j = j + 1
        elif P[index][0]==P[index+1][0] and P[index][1]==P[index+1][1] :
            pass
        else:
            s1_aligned = s1_aligned + s1[i]
            s2_aligned = s2_aligned + s2[j]
            i = i + 1
            j = j + 1
        index = index+1
        
        #print(s1_aligned)
        #print(s2_aligned)
        wf = [s1_aligned, s2_aligned]
        
    return s1_aligned, s2_aligned


s1, s2, output_file = parse_input()
P = perform_alignment_dc(s1, s2, 0, 0)
P.sort(key = lambda x:(x[0],x[1]))
s1_aligned, s2_aligned = get_string_DC(P,s1,s2)
print(s1_aligned)
print(s2_aligned)