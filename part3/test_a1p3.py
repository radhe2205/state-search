# !/usr/bin/env python3
# YOU SHOULD NOT MODIFY THIS FILE
# 
# test_a1p3.py version 2021.02.24
#
# Rushabh Shah


'''test_choose_team.py

Usage: 
python3 test_choose_team.py user1-user2-user3-a1/part3

It is not always possible to get the best solution so we will check whether the solution is below a threshold in order to pass the test case.

For final grading we will be using more complex test cases.
'''
import pytest
import numpy as np
import assign
time_ = 100

def get_solution(test_file):

	result = []

	for i in assign.solver(test_file):

		result.append([i['assigned-groups'],i['total-cost']])

	return result

def check_names(test_file,result):
	names_ = [j for i in [i.split('-') for i in result[0]] for j in i]
	
	names = set(names_)
	with  open(test_file,'r') as f:
		
		original_names = set()
		for i in f.readlines():
			original_names.add(i.split()[0])

	return (original_names==names and len(names)==len(original_names))

def check_solution(test_file,result,threshold = float('inf')):

	assert len(result) != 0, "No solution found"

	assert check_names(test_file,result[-1]) == True, 'Everyone should be assigned to a team'

	assert type(result[-1][1]) in (int,float), 'TypeError'

	assert result[-1][1] <= threshold, 'The cost is incorrect, it could be better'


@pytest.mark.timeout(time_)
def test_case_1():
	check_solution('test1.txt',get_solution('test1.txt'),10)


@pytest.mark.timeout(time_)
def test_case_2():
	check_solution('test2.txt',get_solution('test2.txt'),15)


@pytest.mark.timeout(time_)
def test_case_3():
	check_solution('test3.txt',get_solution('test3.txt'))  ## there is no threshold for this case. 