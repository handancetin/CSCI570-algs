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
        i = i + 1

    i = 0
    s2 = input_strings[1]
    while i < len(num2):
        s2 = s2[0:num2[i]+1] + s2 + s2[num2[i]+1 :]
        i = i + 1
    return s1, s2, output_file

def perform_alignment_dp(s1, s2):
    OPT = np.zeros((len(s1) + 1, len(s2) + 1))

    for i in range(1, len(s1) + 1):
        OPT[i][0] = gap_penalty * i

    for j in range(1, len(s2) + 1):
        OPT[0][j] = gap_penalty * j

    s1 = 'x' + s1
    s2 = 'x' + s2

    for i in range(1, len(s1)):
        for j in range(1, len(s2)):
            OPT[i][j] = min(OPT[i][j-1] + gap_penalty,
                            OPT[i-1][j] + gap_penalty,
                            OPT[i-1][j-1] + mismatch_penalty(s1[i], s2[j]))

    return OPT

def perform_alignment_dp_rev(s1, s2):

    s1 = ' ' + s1
    s2 = ' ' + s2

    OPT = np.zeros((len(s1), 2))
    for i in range(len(s1)):
        OPT[i][0] = i * gap_penalty
    OPT[0][1] = gap_penalty

    j = 1
    while j < len(s2):
        for i in range(1, len(s1)):
            OPT[i][1] = min(OPT[i-1][1] + gap_penalty,
                            OPT[i][0] + gap_penalty,
                            OPT[i-1][0] + mismatch_penalty(s1[i], s2[j]))
        j = j + 1

        OPT[:, 0] = OPT[:, 1]
        OPT[:, 1] = 0
        OPT[0][1] = j * gap_penalty

    return OPT


def get_path(s1, s2, OPT):
    s1 = ' ' + s1
    s2 = ' ' + s2

    i = len(s1) - 1
    j = len(s2) - 1

    t1 = []
    t2 = []

    while i > 0 and j > 0:
        move_hor = OPT[i][j - 1] + gap_penalty
        move_ver = OPT[i - 1][j] + gap_penalty
        move_cro = OPT[i - 1][j - 1] + mismatch_penalty(s1[i], s2[j])

        movement = min(move_hor, move_ver, move_cro)
        if move_cro == movement:
            t1.append(s1[i])
            t2.append(s2[j])
            i = i - 1
            j = j - 1
        elif move_ver == movement:
            t1.append(s1[i])
            t2.append('_')
            i = i - 1
        else:
            t1.append('_')
            t2.append(s2[j])
            j = j - 1

    while i > 0:
        t1.append(s1[i])
        t2.append('_')
        i = i - 1

    while j > 0:
        t1.append('_')
        t2.append(s2[j])
        j = j - 1

    t1 = ''.join(reversed(t1))
    t2 = ''.join(reversed(t2))

    return t1, t2

def perform_alignment_dc(s1, s2):
    s1_length = len(s1)
    s2_length = len(s2)

    if s1_length <= 2 or s2_length <= 2:
        OPT = perform_alignment_dp(s1, s2)
        return get_path(s1, s2, OPT)

    min_index = np.inf
    min_sum = np.inf

    c1 = perform_alignment_dp_rev(s1,       s2[:s2_length // 2])
    c2 = perform_alignment_dp_rev(s1[::-1], s2[s2_length // 2:][::-1])

    c2 = c2[::-1]

    for idx in range(c2.shape[0]):
        s = c1[idx][0] + c2[idx][0]
        if s < min_sum:
            min_sum = s
            min_index = idx

    s1_left, s2_left = perform_alignment_dc(s1[:min_index], s2[:s2_length // 2])
    s1_right, s2_right = perform_alignment_dc(s1[min_index:], s2[s2_length // 2:])
    s1_aligned = s1_left + s1_right
    s2_aligned = s2_left + s2_right

    return s1_aligned, s2_aligned

def calculate_cost(s1_aligned, s2_aligned):
    cost = 0
    for i in range(len(s1_aligned)):
        if s1_aligned[i] == '_' or s2_aligned[i] == '_':
            cost = cost + gap_penalty
        else:
            cost = cost + mismatch_penalty(s1_aligned[i], s2_aligned[i])
    return cost


## RUNNER CODE
start_time = time.process_time()
start_memory = process_memory()

s1, s2, output_file = parse_input()
s1_aligned, s2_aligned = perform_alignment_dc(s1, s2)
cost = calculate_cost(s1_aligned, s2_aligned)
    
end_memory = process_memory()
end_time = time.process_time()

used_memory = end_memory - start_memory
runtime = end_time - start_time

# write the output
output_data = [str(cost)+ '\n', 
                s1_aligned + '\n', 
                s2_aligned + '\n', 
                str(runtime) + '\n', 
                str(used_memory)]
f = open(output_file, 'w')
f.writelines(output_data)
f.close()