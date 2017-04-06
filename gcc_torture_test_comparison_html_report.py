# Import section:
#########################################
import os
import sys
import commands
import shutil
import time
import platform
import re
from prettytable import PrettyTable
#########################################

# Command line arguments:
###################################################################################
path = sys.argv
if len(sys.argv) != 3:
	print "Invalid param mentioned"
	print "Input should be like this: python extract.py <file_name> "
	exit()
###################################################################################

# file_contents_pass=[]
# file_contents_fail=[]
# file_contents_unsupported=[]
# file_contents_testing=[]

list_of_gcc_test_case_names = []
list_of_gcc_test_case_names_w_flags = []
dict_of_gcc_test_case_names_w_flags = {} 
list_of_clang_test_case_names = []
list_of_clang_test_case_names_w_flags = []
dict_of_clang_test_case_names_w_flags = {} 

known_pass_case = []
known_fail_case = []
regression_case = []
progression_case = []
missing_clang_case = []
missing_gcc_case = []

dict_known_pass_case = {}
dict_known_fail_case = {}
dict_regression_case = {}
dict_progression_case = {}
dict_missing_clang_case = {}
dict_missing_gcc_case = {}

def create_extract_testing_files(file_name):
	# print "i am here"
	my_file = open(file_name)
	a = my_file.read()
	# print(file_contents)
	file_contents = a.split("\n")

	extract = open(file_name.split(".")[0]+"_extract.txt", "w")
	testing = open(file_name.split(".")[0]+"_testing.txt", "w")

	for i in range(0,len(file_contents)):
		if (re.match(r'^PASS.*', file_contents[i])):
			# if (file_contents[i].split()[-1] == "test"):
			# file_contents_pass.append(file_contents[i])
			# print file_contents[i]
			extract.write(file_contents[i])
			extract.write("\n")
		elif (re.match(r'^FAIL.*', file_contents[i])):
			# if (file_contents[i].split()[-1] == "test"):
			# file_contents_fail.append(file_contents[i])
			# print file_contents[i]
			extract.write(file_contents[i])
			extract.write("\n")
		elif (re.match(r'^UNSUPPORTED.*', file_contents[i])):
			# file_contents_unsupported.append(file_contents[i])
			# print file_contents[i]
			extract.write(file_contents[i])
			extract.write("\n")
		else:
			pass
			
		if (re.match(r'^Testing.execute.*', file_contents[i])):
			# file_contents_testing.append(file_contents[i])
			# print file_contents[i]
			testing.write(file_contents[i])
			testing.write("\n")
			
	my_file.close()
	extract.close()
	testing.close()
	# print file_contents_pass
	# print file_contents_fail
	# print file_contents_unsupported



def get_count_of_diff_test_cases(file_name):
	
	d = {}
	l = []
	test_case_names = []
	pass_count = 0
	fail_count = 0
	unsupported_count = 0
	unknown_count = 0
	key_count = 0
	
	my_file = open(file_name.split(".")[0]+"_testing.txt")
	a = my_file.read()
	# print(file_contents)
	file_contents = a.split("\n")

	for i in range(0,len(file_contents)):
		if (re.match(r'^Testing.*', file_contents[i])):
			test_case_names.append(file_contents[i].split()[1].split(",")[0])
			temp = [file_contents[i].split()[1].split(",")[0],'_'.join(file_contents[i].split(",")[1].split())]
			l.append(':'.join(temp))
			d[':'.join(temp)] = ""
			# print "d["+':'.join(temp)+"] is ",d[':'.join(temp)]
			
	my_file.close()
	# print "d before : ",d

	for key in d.keys():
		pattern = key.split(":")[0]+"   "+' '.join(key.split(":")[1].split("_"))+"  "
		cmd = "grep '"+pattern+"' "+file_name.split(".")[0]+"_extract.txt"+""
		ret,op = commands.getstatusoutput(cmd)
		if (op == ''):
			pattern = key.split(":")[0]+"   "+' '.join(key.split(":")[1].split("_"))
			cmd = "grep '"+pattern+"' "+file_name.split(".")[0]+"_extract.txt"+""
			ret,op = commands.getstatusoutput(cmd)
		if (len(op.split("\n")) == 1):
			d[key] = op.split("\n")[0].split()[0].split(":")[0]
			if (op.split("\n")[0].split()[0].split(":")[0] == "PASS"):
				pass_count = pass_count + 1
			elif (op.split("\n")[0].split()[0].split(":")[0] == "FAIL"):
				fail_count = fail_count + 1
			elif (op.split("\n")[0].split()[0].split(":")[0] == "UNSUPPORTED"):
				unsupported_count = unsupported_count + 1
		elif (len(op.split("\n")) == 2):
			temp1 = op.split("\n")[0].split()[0].split(":")[0]+"_"+op.split("\n")[1].split()[0].split(":")[0]
			if (temp1 == "PASS_PASS"):
				d[key] = "PASS"
				pass_count = pass_count + 1
			elif(temp1 == "PASS_FAIL"):
				d[key] = "FAIL"
				fail_count = fail_count + 1
			elif(temp1 == "FAIL_PASS"):
				d[key] = "UNKNOWN"
				unknown_count = unknown_count + 1
			elif(temp1 == "FAIL_FAIL"):
				d[key] = "FAIL"
				fail_count = fail_count + 1
		elif (len(op.split("\n")) >= 3):
			print "Issue with this pattern : ",pattern

	# print "d after : ",d
	# for key in d.keys():
		# if (d[key] == ''):
			# d[key] = "NULL"
		# print "\nd["+key+"] = "+d[key]
		# key_count = key_count + 1
	# print "List : ",l
	# print "All test case names : ",test_case_names
	
	# print "Total count of test cases with out flags : ",len(set(test_case_names))
	# print "Total count of test cases with flags : ",len(l)
	# print "Total passed test cases with flags : ",pass_count
	# print "Total failed test cases with flags : ",fail_count
	# print "Total unsupported test cases with flags : ",unsupported_count
	# print "Total unknown test cases with flags : ",unknown_count
	# print "Total key's count : ",key_count
	count = [len(set(test_case_names)),len(l),pass_count,fail_count,unsupported_count,unknown_count,pass_count+fail_count+unsupported_count+unknown_count]
	if (len(l) == (pass_count+fail_count+unsupported_count+unknown_count)):
		# print "Test case count balanced."
		pass
	
	return (sorted(set(test_case_names)),l,d,count)

def list_count(list_of_gcc_test_case_names,list_of_clang_test_case_names):

	count1 = 0
	for i in range(0,len(list_of_gcc_test_case_names)):
		for j in range(0,len(list_of_clang_test_case_names)):
			if (list_of_gcc_test_case_names[i] == list_of_clang_test_case_names[j]):
				count1 = count1 + 1
				break
	if (count1 == len(list_of_gcc_test_case_names)):
		print "count with gcc is fine"
		pass
		
	count2 = 0
	for i in range(0,len(list_of_clang_test_case_names)):
		for j in range(0,len(list_of_gcc_test_case_names)):
			if (list_of_gcc_test_case_names[i] == list_of_clang_test_case_names[j]):
				count2 = count2 + 1
				break
	if (count2 == len(list_of_clang_test_case_names)):
		print "count with clang is fine"
		pass
	if (count1 == count2):
		print "Both gcc and clang test cases are same."

def compare_gcc_clang(list_of_gcc_test_case_names_w_flags,list_of_clang_test_case_names_w_flags,dict_of_gcc_test_case_names_w_flags,dict_of_clang_test_case_names_w_flags):
	
	for i in range(0,len(list_of_gcc_test_case_names_w_flags)):
		count1 = 0
		for j in range(0,len(list_of_clang_test_case_names_w_flags)):
			if (list_of_gcc_test_case_names_w_flags[i] == list_of_clang_test_case_names_w_flags[j]):
				if (dict_of_gcc_test_case_names_w_flags[list_of_gcc_test_case_names_w_flags[i]] == "PASS" and dict_of_clang_test_case_names_w_flags[list_of_clang_test_case_names_w_flags[j]] == "PASS"):
					known_pass_case.append(list_of_clang_test_case_names_w_flags[j])
					dict_known_pass_case[list_of_clang_test_case_names_w_flags[j]] = dict_of_clang_test_case_names_w_flags[list_of_clang_test_case_names_w_flags[j]]
				elif (dict_of_gcc_test_case_names_w_flags[list_of_gcc_test_case_names_w_flags[i]] == "PASS" and dict_of_clang_test_case_names_w_flags[list_of_clang_test_case_names_w_flags[j]] == "FAIL"):
					regression_case.append(list_of_clang_test_case_names_w_flags[j])
					dict_regression_case[list_of_clang_test_case_names_w_flags[j]] = dict_of_clang_test_case_names_w_flags[list_of_clang_test_case_names_w_flags[j]]
				elif (dict_of_gcc_test_case_names_w_flags[list_of_gcc_test_case_names_w_flags[i]] == "FAIL" and dict_of_clang_test_case_names_w_flags[list_of_clang_test_case_names_w_flags[j]] == "FAIL"):
					known_fail_case.append(list_of_clang_test_case_names_w_flags[j])
					dict_known_fail_case[list_of_clang_test_case_names_w_flags[j]] = dict_of_clang_test_case_names_w_flags[list_of_clang_test_case_names_w_flags[j]]
				elif (dict_of_gcc_test_case_names_w_flags[list_of_gcc_test_case_names_w_flags[i]] == "FAIL" and dict_of_clang_test_case_names_w_flags[list_of_clang_test_case_names_w_flags[j]] == "PASS"):
					progression_case.append(list_of_clang_test_case_names_w_flags[j])
					dict_progression_case[list_of_clang_test_case_names_w_flags[j]] = dict_of_clang_test_case_names_w_flags[list_of_clang_test_case_names_w_flags[j]]
				elif (dict_of_gcc_test_case_names_w_flags[list_of_gcc_test_case_names_w_flags[i]] == "PASS" and (dict_of_clang_test_case_names_w_flags[list_of_clang_test_case_names_w_flags[j]] == "UNKNOWN" or dict_of_clang_test_case_names_w_flags[list_of_clang_test_case_names_w_flags[j]] == "UNSUPPORTED")):
					regression_case.append(list_of_clang_test_case_names_w_flags[j])
					dict_regression_case[list_of_clang_test_case_names_w_flags[j]] = dict_of_clang_test_case_names_w_flags[list_of_clang_test_case_names_w_flags[j]]
				elif (dict_of_gcc_test_case_names_w_flags[list_of_gcc_test_case_names_w_flags[i]] == "FAIL" and (dict_of_clang_test_case_names_w_flags[list_of_clang_test_case_names_w_flags[j]] == "UNKNOWN" or dict_of_clang_test_case_names_w_flags[list_of_clang_test_case_names_w_flags[j]] == "UNSUPPORTED")):
					known_fail_case.append(list_of_clang_test_case_names_w_flags[j])
					dict_known_fail_case[list_of_clang_test_case_names_w_flags[j]] = dict_of_clang_test_case_names_w_flags[list_of_clang_test_case_names_w_flags[j]]
				elif ((dict_of_gcc_test_case_names_w_flags[list_of_gcc_test_case_names_w_flags[i]] == "UNKNOWN" or dict_of_gcc_test_case_names_w_flags[list_of_gcc_test_case_names_w_flags[i]] == "UNSUPPORTED") and (dict_of_clang_test_case_names_w_flags[list_of_clang_test_case_names_w_flags[j]] == "UNKNOWN" or dict_of_clang_test_case_names_w_flags[list_of_clang_test_case_names_w_flags[j]] == "UNSUPPORTED")):
					known_fail_case.append(list_of_clang_test_case_names_w_flags[j])
					dict_known_fail_case[list_of_clang_test_case_names_w_flags[j]] = dict_of_clang_test_case_names_w_flags[list_of_clang_test_case_names_w_flags[j]]
				elif ((dict_of_gcc_test_case_names_w_flags[list_of_gcc_test_case_names_w_flags[i]] == "UNKNOWN" or dict_of_gcc_test_case_names_w_flags[list_of_gcc_test_case_names_w_flags[i]] == "UNSUPPORTED") and (dict_of_clang_test_case_names_w_flags[list_of_clang_test_case_names_w_flags[j]] == "PASS")):
					progression_case.append(list_of_clang_test_case_names_w_flags[j])
					dict_progression_case[list_of_clang_test_case_names_w_flags[j]] = dict_of_clang_test_case_names_w_flags[list_of_clang_test_case_names_w_flags[j]]
				elif ((dict_of_gcc_test_case_names_w_flags[list_of_gcc_test_case_names_w_flags[i]] == "UNKNOWN" or dict_of_gcc_test_case_names_w_flags[list_of_gcc_test_case_names_w_flags[i]] == "UNSUPPORTED") and (dict_of_clang_test_case_names_w_flags[list_of_clang_test_case_names_w_flags[j]] == "FAIL")):
					known_fail_case.append(list_of_clang_test_case_names_w_flags[j])
					dict_known_fail_case[list_of_clang_test_case_names_w_flags[j]] = dict_of_clang_test_case_names_w_flags[list_of_clang_test_case_names_w_flags[j]]
				count1 = 1
				break
		if (count1 == 0):
			missing_gcc_case.append(list_of_gcc_test_case_names_w_flags[i])
			dict_missing_gcc_case[list_of_gcc_test_case_names_w_flags[i]] = dict_of_gcc_test_case_names_w_flags[list_of_gcc_test_case_names_w_flags[i]]

	
	for i in range(0,len(list_of_clang_test_case_names_w_flags)):
		count2 = 0
		for j in range(0,len(list_of_gcc_test_case_names_w_flags)):
			if (list_of_clang_test_case_names_w_flags[i] == list_of_gcc_test_case_names_w_flags[j]):
				count2 = 1
		if (count2 == 0):
			missing_clang_case.append(list_of_clang_test_case_names_w_flags[i])
			dict_missing_clang_case[list_of_clang_test_case_names_w_flags[i]] = dict_of_clang_test_case_names_w_flags[list_of_clang_test_case_names_w_flags[i]]
			
	# print "Total Regressions : ",len(regression_case)
	# print "Total Progressions : ",len(progression_case)
	# print "Total Known cases : ",len(known_fail_case)
	# print "Total Success cases : ",len(known_pass_case)
	# print "Total Missing GCC cases : ",len(missing_gcc_case)
	# print "Total Missing Clang cases : ",len(missing_clang_case)
	
	t = 0	
	t = HTML.Table(header_row= HTML.TableRow(["Regressions","Progressions","Known cases","Success cases","Missing GCC cases","Missing Clang cases"], bgcolor='LightGrey'))
	count = [len(regression_case),len(progression_case),len(known_fail_case),len(known_pass_case),len(missing_gcc_case),len(missing_clang_case)]
	t.add_row(count)
	print t
	
	if (len(list_of_clang_test_case_names_w_flags) == (len(regression_case)+len(progression_case)+len(known_fail_case)+len(known_pass_case)+len(missing_clang_case))):
		# print "Work done."
		pass

def tabular_print(case_list,case_dict):
	t = 0
	s_no = 0
	t = PrettyTable(["S/No","Test_case_name","Flag","Result"])
	for i in range(0,len(case_list)):
		s_no = s_no + 1
		Test_case_name = case_list[i].split(":")[0]
		Flag = ' '.join(case_list[i].split(":")[1].split("_"))
		Result = case_dict[case_list[i]]
		row = [s_no,Test_case_name,Flag,Result]
		t.add_row(row)
	print t

def html_tabular_print(case_list,case_dict):
	t = 0
	s_no = 0
	t = HTML.Table(header_row= HTML.TableRow(["S/No","Test_case_name","Flag","Result"], bgcolor='LightGrey'))

	for i in range(0,len(case_list)):
		s_no = s_no + 1
		Test_case_name = case_list[i].split(":")[0]
		Flag = ' '.join(case_list[i].split(":")[1].split("_"))
		Result = case_dict[case_list[i]]
		row = [s_no,Test_case_name,Flag,Result]
		t.rows.append(row)
	print t

def tabular_count_print(gcc_count,clang_count):
	t = 0	
	t = PrettyTable(["Compilers","Total_test_cases_with_out_flags","Total_test_cases_with_flags_expected","Passed_test_cases","Failed_test_cases","Unsuppoerted_test_cases","Unknown_test_cases","Total_test_cases_with_flags_came"])
	temp1 = ["GCC"]+gcc_count
	t.add_row(temp1)
	temp2 = ["Clang"]+clang_count
	t.add_row(temp2)
	print t

def html_tabular_count_print(gcc_count,clang_count):
	t = 0	
	t = HTML.Table(header_row= HTML.TableRow(["Compilers","Total_test_cases_with_out_flags","Total_test_cases_with_flags_expected","Passed_test_cases","Failed_test_cases","Unsuppoerted_test_cases","Unknown_test_cases","Total_test_cases_with_flags_came"], bgcolor='LightGrey'))
	temp1 = ["GCC"]+gcc_count
	t.rows.append(temp1)
	temp2 = ["Clang"]+clang_count
	t.rows.append(temp2)
	print t	
	
# print "\nFor gcc : "
create_extract_testing_files(path[1])
(list_of_gcc_test_case_names,list_of_gcc_test_case_names_w_flags,dict_of_gcc_test_case_names_w_flags,gcc_count) = get_count_of_diff_test_cases(path[1])

# print "\nFor Clang : "
create_extract_testing_files(path[2])
(list_of_clang_test_case_names,list_of_clang_test_case_names_w_flags,dict_of_clang_test_case_names_w_flags,clang_count) = get_count_of_diff_test_cases(path[2])

print "Gcc and Clang count table : "
tabular_count_print(gcc_count,clang_count)

print "\nCount test : "
list_count(list_of_gcc_test_case_names,list_of_clang_test_case_names)

print "\nCompare list : "
compare_gcc_clang(list_of_gcc_test_case_names_w_flags,list_of_clang_test_case_names_w_flags,dict_of_gcc_test_case_names_w_flags,dict_of_clang_test_case_names_w_flags)

print "\nRegressions : "
tabular_print(regression_case,dict_regression_case)
print "\nProgressions : "
tabular_print(progression_case,dict_progression_case)
print "\nMissing GCC cases : "
tabular_print(missing_gcc_case,dict_missing_gcc_case)
print "\nMissing Clang cases : "
tabular_print(missing_clang_case,dict_missing_clang_case)
print "\nKnown cases : "
tabular_print(known_fail_case,dict_known_fail_case)
print "\nSuccess cases : "
tabular_print(known_pass_case,dict_known_pass_case)
