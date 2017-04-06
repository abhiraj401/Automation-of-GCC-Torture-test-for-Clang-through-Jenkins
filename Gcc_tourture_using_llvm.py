#!/usr/bin/env python
'''
Author : ABHIRAJ.G
Email id : abhiraj.garakapati@gmail.com

Input should be like this: 
python -W ignore test_gcc_torture_using_llvm.py <gcc/g++/clang/clang++> <execute.exp/compile.exp> <optional : intermediate_staging_build_number>

Example:
python -W ignore test_gcc_torture_using_llvm.py gcc execute.exp

(Automated way of generating respective log file and comparing the result with previous version and generating a html file which contains: count of test cases, count of regressions, progressions, etc.)
'''

# Import section:
#########################################
import os
import sys
import commands
import shutil
import time
import platform
import re
import MySQLdb
import jenkinsapi
from jenkinsapi.jenkins import Jenkins
#########################################

# Command line arguments:
#####################################################################################################################################
path = sys.argv
if len(sys.argv) == 4:
	pass
elif len(sys.argv) == 5:
	intermediate_staging_build_number = path[4]
	print intermediate_staging_build_number
else:
	print "Invalid param mentioned"
	print "Input should be like this: python test_gcc_torture_using_llvm.py <gcc/g++/clang/clang++> <execute.exp/compile.exp> <MAINLINE/STAGING> <optional : intermediate_staging/mainline_build_number>"
	exit()
#####################################################################################################################################
 
# Define variables
##################################################
gcc_or_clang  = path[1] 
test_name  = path[2] 
Mainline_or_Staging = path[3]
local_path = os.getenv("PATH")
WORKSPACE = os.popen('pwd').read().split()[0]
##################################################

# Setting paths.
######################################
print "local path : ",local_path
print "Workspace path : ",WORKSPACE
######################################

# Creating output log directory.
######################################################
try:
	os.system('mkdir $WORKSPACE/execute_logs')
except Exception:
	os.system('mkdir execute_logs')
###################################################### 
 
# Jenkins section to get dragonegg version for given staging build.
#########################################################################################################
if len(sys.argv) == 5:
	if (Mainline_or_Staging == "MAINLINE"):
		J = Jenkins('http://bgl-buildmaster.amd.com:8080/')
		for i in range(J['CPUPC_Dragonegg-Redhat_Mainline_Branch'].get_last_stable_buildnumber(),J['CPUPC_Dragonegg-Redhat_Mainline_Branch'].get_first_buildnumber(),-1):
			console_content = J['CPUPC_Dragonegg-Redhat_Mainline_Branch'].get_build(i).get_console()
			staging_build_number = console_content.split("\n")[0].split()[-1]
			print str(staging_build_number)+" is "+str(i)
			if (str(staging_build_number) == str(intermediate_staging_build_number)):
				dragonegg_build_number = i
				print "dragonegg_build_number is "+str(dragonegg_build_number)
				break
	else:
		J = Jenkins('http://bgl-buildmaster.amd.com:8080/')
		for i in range(J['CPUPC_Dragonegg-Redhat_Staging_Branch'].get_last_stable_buildnumber(),J['CPUPC_Dragonegg-Redhat_Staging_Branch'].get_first_buildnumber(),-1):
			console_content = J['CPUPC_Dragonegg-Redhat_Staging_Branch'].get_build(i).get_console()
			staging_build_number = console_content.split("\n")[0].split()[-1]
			print str(staging_build_number)+" is "+str(i)
			if (str(staging_build_number) == str(intermediate_staging_build_number)):
				dragonegg_build_number = i
				print "dragonegg_build_number is "+str(dragonegg_build_number)
				break
######################################################################################################### 

# Copying and Unzipping respective complier.
########################################################################################################
if len(sys.argv) == 5:
	if ((gcc_or_clang == "clang") or (gcc_or_clang == "clang++")):
		if (Mainline_or_Staging == "MAINLINE"):
			#Step:Copying compiler and DragonEgg for test
			for i in range(0,len(J['CPUPC_Mainline_Branch'].get_build(int(intermediate_staging_build_number)).get_artifact_dict().keys())):
				if (re.match(r'^LLVM-MAINLINE-BUILD*', J['CPUPC_Mainline_Branch'].get_build(int(intermediate_staging_build_number)).get_artifact_dict().keys()[i])):
					mainline_build = J['CPUPC_Mainline_Branch'].get_build(int(intermediate_staging_build_number)).get_artifact_dict().keys()[i]

			mainline_dragonegg_build = J['CPUPC_Dragonegg-Redhat_Mainline_Branch'].get_build(dragonegg_build_number).get_artifact_dict().keys()[0]
			
			os.system('wget http://bgl-buildmaster.amd.com:8080/job/CPUPC_Mainline_Branch/'+str(intermediate_staging_build_number)+'/artifact/'+str(mainline_build)+'')
			os.system('wget http://bgl-buildmaster.amd.com:8080/job/CPUPC_Dragonegg-Redhat_Mainline_Branch/'+str(dragonegg_build_number)+'/artifact/'+str(mainline_dragonegg_build)+'')
			try:
				tar_file1 = os.popen('ls -f *.tar.gz').read()
			except Exception:
				tar_file1 = os.popen('ls -f *.tar.gz').read()
			#Step:Untar compiler and DragonEgg
			for i in range(0,len(tar_file1.split())):
				print "Unzipping : ",tar_file1.split()[i].split("/")[-1]
				unzip_output1 = os.popen('tar -xvf '+tar_file1.split()[i].split("/")[-1]+'').read()
		else:
			#Step:Copying compiler and DragonEgg for test
			os.system('wget http://bgl-buildmaster.amd.com:8080/job/CPUPC_Staging_Redhat/'+str(intermediate_staging_build_number)+'/artifact/LLVM-STAGING-BUILD-'+str(intermediate_staging_build_number)+'.tar.gz')
			os.system('wget http://bgl-buildmaster.amd.com:8080/job/CPUPC_Dragonegg-Redhat_Staging_Branch/'+str(dragonegg_build_number)+'/artifact/Dragonegg-Redhat_Staging-BUILD-'+str(dragonegg_build_number)+'.tar.gz')
			try:
				tar_file1 = os.popen('ls -f *.tar.gz').read()
			except Exception:
				tar_file1 = os.popen('ls -f *.tar.gz').read()
			#Step:Untar compiler and DragonEgg
			for i in range(0,len(tar_file1.split())):
				print "Unzipping : ",tar_file1.split()[i].split("/")[-1]
				unzip_output1 = os.popen('tar -xvf '+tar_file1.split()[i].split("/")[-1]+'').read()

else:
	if ((gcc_or_clang == "clang") or (gcc_or_clang == "clang++")):
		#Step:Copying compiler and DragonEgg for test
		os.system('cp -f /home/amd/mnt/jenkins_perf_proj_stage_comp/* .')
		tar_file1 = os.popen('ls -f /home/amd/mnt/jenkins_perf_proj_stage_comp/*').read()
		#Step:Untar compiler and DragonEgg
		for i in range(0,len(tar_file1.split())):
			print "Unzipping : ",tar_file1.split()[i].split("/")[-1]
			unzip_output1 = os.popen('tar -xvf '+tar_file1.split()[i].split("/")[-1]+'').read()

	elif (gcc_or_clang == "clang_mirror"):		
		#Mirror build.
		tar_file = os.popen('ls -f '+WORKSPACE+'/LLVM*').read()
		print "Unzipping : ",tar_file.split()[0].split("/")[-1]
		unzip_output = os.popen('tar -xvf '+tar_file.split()[0].split("/")[-1]+'').read()
		#Step:Copying compiler and DragonEgg for test
		os.system('cp -f /home/amd/mnt/jenkins_perf_proj_stage_comp/Dragonegg* .')
		tar_file1 = os.popen('ls -f /home/amd/mnt/jenkins_perf_proj_stage_comp/*').read()
		#Step:Untar compiler and DragonEgg
		for i in range(0,len(tar_file1.split())):
			# if re.match(r'LLVM.*', tar_file1.split()[i].split("/")[-1]):
				# pass
			# else:
			print "Unzipping : ",tar_file1.split()[i].split("/")[-1]
			unzip_output1 = os.popen('tar -xvf '+tar_file1.split()[i].split("/")[-1]+'').read()
		
			
	elif ((gcc_or_clang == "gcc") or (gcc_or_clang == "g++")):
		#gcc compiler.
		os.system('cp -f /home/amd/mnt/testsuites/install_gcc-6.1.0.tar .')
		tar_file3 = os.popen('ls -f /home/amd/mnt/testsuites/install_gcc-6.1.0.tar').read()
		#Step:Untar gcc compiler.
		for i in range(0,len(tar_file3.split())):
			print "Unzipping : ",tar_file3.split()[i].split("/")[-1]
			unzip_output3 = os.popen('tar -xvf '+tar_file3.split()[i].split("/")[-1]+'').read()
########################################################################################################

# Copying test suite and untar it.
#######################################################################################################
os.system('cp -f /home/qa/AQI/GROUPS/app_no_child/gcc_6.1.0_torture_test/* .')
tar_file2 = os.popen('ls -f /home/qa/AQI/GROUPS/app_no_child/gcc_6.1.0_torture_test/*').read()
print "Unzipping : ",tar_file2.split()[0].split("/")[-1]
unzip_output2 = os.popen('tar -xvf '+tar_file2.split()[0].split("/")[-1]+'').read()
#######################################################################################################

# Setting respective environment variables.
#######################################################################################################
if ((gcc_or_clang == "clang") or (gcc_or_clang == "clang++")):
	
	os.system('echo Before: $PATH')
	if (Mainline_or_Staging == "MAINLINE"):
		if re.match(r'LLVM.*', tar_file1.split()[0].split("/")[-1]):
			STAGING_BUILD = tar_file1.split()[0].split("/")[-1].split("_FROM_STAGING")[0].split("LLVM-")[1]
			os.environ["PATH"] = WORKSPACE+"/"+STAGING_BUILD+"/bin:"+local_path
		elif re.match(r'LLVM.*', tar_file1.split()[1].split("/")[-1]):
			STAGING_BUILD = tar_file1.split()[1].split("/")[-1].split("_FROM_STAGING")[0].split("LLVM-")[1]
			os.environ["PATH"] = WORKSPACE+"/"+STAGING_BUILD+"/bin:"+local_path
		print "i am here ",STAGING_BUILD
	else:
		if re.match(r'LLVM.*', tar_file1.split()[0].split("/")[-1]):
			STAGING_BUILD = tar_file1.split()[0].split("/")[-1].split(".tar.gz")[0].split("LLVM-")[1]
			os.environ["PATH"] = WORKSPACE+"/"+STAGING_BUILD+"/bin:"+local_path
		elif re.match(r'LLVM.*', tar_file1.split()[1].split("/")[-1]):
			STAGING_BUILD = tar_file1.split()[1].split("/")[-1].split(".tar.gz")[0].split("LLVM-")[1]
			os.environ["PATH"] = WORKSPACE+"/"+STAGING_BUILD+"/bin:"+local_path
		
	os.system('echo After: $PATH')

elif (gcc_or_clang == "clang_mirror"):
	os.system('echo Before: $PATH')
	
	if re.match(r'LLVM.*', tar_file.split()[0].split("/")[-1]):
		STAGING_BUILD = tar_file.split()[0].split("/")[-1].split(".tar.gz")[0].split("LLVM-")[1]
		os.environ["PATH"] = WORKSPACE+"/"+STAGING_BUILD+"/bin:"+local_path
		
	os.system('echo After: $PATH')
	
elif ((gcc_or_clang == "gcc") or (gcc_or_clang == "g++")):

	GCCPATH = WORKSPACE+"/"+tar_file3.split()[0].split("/")[-1].split(".tar")[0]
	print "GCCPATH : ",GCCPATH
	GCCVER = "6.1.0"
	GCCARCH = "x86_64-unknown-linux-gnu"

	# os.system('echo GCC_EXEC_PREFIX Before: $GCC_EXEC_PREFIX')
	os.system('echo LIBRARY_PATH Before: $LIBRARY_PATH')
	os.system('echo LD_RUN_PATH Before: $LD_RUN_PATH')
	os.system('echo PATH Before: $PATH')
	os.system('echo MANPATH Before: $MANPATH')
	os.system('echo INFOPATH Before: $INFOPATH')
	os.system('echo LD_LIBRARY_PATH Before: $LD_LIBRARY_PATH')

	# GCC_EXEC_PREFIX = os.getenv("GCC_EXEC_PREFIX")
	LIBRARY_PATH = os.getenv("LIBRARY_PATH")
	LD_RUN_PATH = os.getenv("LD_RUN_PATH")
	PATH = os.getenv("PATH")
	MANPATH = os.getenv("MANPATH")
	INFOPATH = os.getenv("INFOPATH")
	LD_LIBRARY_PATH = os.getenv("LD_LIBRARY_PATH")
	
	# os.environ["GCC_EXEC_PREFIX"] = GCCPATH
	os.environ["LIBRARY_PATH"] = GCCPATH+"/lib:"+GCCPATH+"/lib64"
	os.environ["LD_RUN_PATH"] = os.getenv("LIBRARY_PATH")
	os.environ["PATH"] = GCCPATH+"/bin:"+GCCPATH+"/libexec/gcc/"+GCCARCH+"/"+GCCVER+":"+ os.getenv("PATH")
	os.environ["MANPATH"] = GCCPATH+"/man:"+ str(MANPATH)
	os.environ["INFOPATH"] = GCCPATH+"/info:"+ str(INFOPATH)
	os.environ["LD_LIBRARY_PATH"] = GCCPATH+"/lib64:"+GCCPATH+"/lib:"+ str(LD_LIBRARY_PATH)

	# os.system('echo GCC_EXEC_PREFIX After: $GCC_EXEC_PREFIX')
	os.system('echo LIBRARY_PATH After: $LIBRARY_PATH')
	os.system('echo LD_RUN_PATH After: $LD_RUN_PATH')
	os.system('echo PATH After: $PATH')
	os.system('echo MANPATH After: $MANPATH')
	os.system('echo INFOPATH After: $INFOPATH')
	os.system('echo LD_LIBRARY_PATH After: $LD_LIBRARY_PATH')
	
#######################################################################################################

# Setting and Printing all parameters.
########################################################################
if (gcc_or_clang == "clang_mirror"):
	gcc_or_clang = "clang"

LLVM_DIR_NAME = tar_file2.split()[0].split("/")[-1].split(".tar")[0]
SUITE_DIR = WORKSPACE+'/'+LLVM_DIR_NAME+'/gcc/testsuite'
RESULT_DIR = WORKSPACE+"/execute_logs"
Redirected_log = gcc_or_clang+"_execute_result.log"
print gcc_or_clang," -v"
version_check= gcc_or_clang+" -v"
ret,op = commands.getstatusoutput(version_check)
print op
if ret != 0:
	print "Execution of version command Failed"
else:
	print "Execution version command passed"
	
print "SUITE_DIR : ",SUITE_DIR
print "RESULT_DIR : ",RESULT_DIR
print "Run INFO: "
print "clang under test: "
print "Torture tests folder: ",SUITE_DIR
print "Test name: execute.exp"
print "Result folder: ",RESULT_DIR
print "Redirected log: ",Redirected_log
########################################################################

# Runcommand.
###################################################################################################################################################
print 'runtest -all --debug -verbose -v2 --tool '+gcc_or_clang+' --srcdir '+SUITE_DIR+' '+test_name+' --outdir '+RESULT_DIR+' &>'+Redirected_log+''
cmd = "runtest -all --debug -verbose -v2 --tool %s --srcdir %s %s --outdir %s &> %s"%(gcc_or_clang,SUITE_DIR,test_name,RESULT_DIR,Redirected_log)
# commands.getstatusoutput(cmd)
# os.system('runtest -all --debug -verbose -v2 --tool '+gcc_or_clang+' --srcdir '+SUITE_DIR+' execute.exp --outdir '+RESULT_DIR+' &>'+Redirected_log+'')
ret,op = commands.getstatusoutput(cmd)
my_file = open(gcc_or_clang+".txt", "w")
my_file.write(op)
if ret != 0:
	print "Execution of command Failed"
else:
	print "Execution pass"
my_file.close()
###################################################################################################################################################

# Coping log files to respective location.
########################################################################################################################################################################
print "clang.log file generated successfully."

os.system('mkdir /home/amd/mnt/gcc_torture_tests/logs/'+STAGING_BUILD+'')
os.system('mkdir /home/amd/mnt/gcc_torture_tests/logs/'+STAGING_BUILD+'/'+test_name+'')
try:
	os.system('cp -f  $WORKSPACE/execute_logs/'+gcc_or_clang+'.log /home/amd/mnt/gcc_torture_tests/logs/'+STAGING_BUILD+'/'+test_name+'/'+gcc_or_clang+'_'+STAGING_BUILD+'.log')
except Exception:
	os.system('cp -f  execute_logs/'+gcc_or_clang+'.log /home/amd/mnt/gcc_torture_tests/logs/'+STAGING_BUILD+'/'+test_name+'/'+gcc_or_clang+'_'+STAGING_BUILD+'.log')

########################################################################################################################################################################

# Fetching revision data.
########################################################################################################################################################################################################

#Connecting to a Database:
####################################################################
con=MySQLdb.connect(db='aqidb',user='qa',host='msdnkvstability',passwd='test123')
####################################################################

#Fetching required data from the database. (Fetchs the compilerRev numbers to a list form.)
########################################################################################################################################################################################
'''
if (Mainline_or_Staging == "MAINLINE"):
	mainline_list = []
	J = Jenkins('http://bgl-buildmaster.amd.com:8080/')
	for i in range(J['CPUPC_Mainline_Branch'].get_last_stable_buildnumber(),J['CPUPC_Mainline_Branch'].get_first_buildnumber(),-1):
		if (J['CPUPC_Mainline_Branch'].get_build(int(i)).is_good()):
			mainline_list.append(i)
			if (int(intermediate_staging_build_number) > int(i)):
				next_build_number = i
				break
					
else:
	staging_list = []
	J = Jenkins('http://bgl-buildmaster.amd.com:8080/')
	for i in range(J['CPUPC_Staging_Redhat'].get_last_stable_buildnumber(),J['CPUPC_Staging_Redhat'].get_first_buildnumber(),-1):
		if (J['CPUPC_Staging_Redhat'].get_build(int(i)).is_good()):
			staging_list.append(i)
			if (int(intermediate_staging_build_number) > int(i)):
				next_build_number = i
				break

'''
build = STAGING_BUILD.split("-")[0]
current = STAGING_BUILD.split("-")[-1]
cur=con.cursor()
if (len(path) == 3):
	if (build=="MAINLINE"):
		cur.execute("select compilerRev from Jobs where ((logDir like '%WeeklyFuncTestingMainline/"+build+"%')and(compilerRev BETWEEN "+(str(int(current)-10))+" AND "+current+")) ORDER BY compilerRev DESC;")
	elif (build=="STAGING"):
		cur.execute("select compilerRev from Jobs where ((logDir like '%"+build+"%')and(compilerRev BETWEEN "+(str(int(current)-10))+" AND "+current+")) ORDER BY compilerRev DESC;")
else:
	if (build=="MAINLINE"):
		cur.execute("select compilerRev from Jobs where ((logDir like '%WeeklyFuncTestingMainline/"+build+"%')and(compilerRev BETWEEN "+(str(int(current)-10))+" AND "+current+")) ORDER BY compilerRev DESC;")
	elif (build=="STAGING"):
		cur.execute("select compilerRev from Jobs where ((logDir like '%"+build+"%')and(compilerRev BETWEEN "+(str(int(current)-10))+" AND "+current+")) ORDER BY compilerRev DESC;")
data_from_db = cur.fetchall()

data_from_db = list(set(data_from_db)) #For converting the tuple to list.
build_list = []

#For converting List elements which are in tuple to list.
for i in range(0,len(data_from_db)):
	tuple_element = int(list(data_from_db[i])[0])
	build_list.append(tuple_element)
	tuple_element = 0

#For sorting the builds in Desending order.
build_list.sort(reverse=True)
print build_list
# '''

if (Mainline_or_Staging == "MAINLINE"):
	STAGING_BUILD_PRE = "MAINLINE-BUILD-"+str(next_build_number)
elif (Mainline_or_Staging == "STAGING"):
	STAGING_BUILD_PRE = "STAGING-BUILD-"+str(next_build_number)

########################################################################################################################################################################################
########################################################################################################################################################################################################

# Creating Report.html file.
#################################################################################################################################################################################################################
print "Creating report.html file."
os.system('mkdir /home/amd/mnt/gcc_torture_tests/reports/'+STAGING_BUILD+'_vs_'+STAGING_BUILD_PRE+'')
os.system('mkdir /home/amd/mnt/gcc_torture_tests/reports/'+STAGING_BUILD+'_vs_'+STAGING_BUILD_PRE+'/'+test_name+'')

os.system('python -W ignore /home/amd/mnt/gcc_torture_tests/torture_test_html.py /home/amd/mnt/gcc_torture_tests/logs/'+STAGING_BUILD_PRE+'/'+test_name+'/'+gcc_or_clang+'_'+STAGING_BUILD_PRE+'.log /home/amd/mnt/gcc_torture_tests/logs/'+STAGING_BUILD+'/'+test_name+'/'+gcc_or_clang+'_'+STAGING_BUILD+'.log > /home/amd/mnt/gcc_torture_tests/reports/'+STAGING_BUILD+'_vs_'+STAGING_BUILD_PRE+'/'+test_name+'/Report.html')

os.system('python -W ignore /home/amd/mnt/gcc_torture_tests/torture_test_html.py /home/amd/mnt/gcc_torture_tests/logs/'+STAGING_BUILD_PRE+'/'+test_name+'/'+gcc_or_clang+'_'+STAGING_BUILD_PRE+'.log /home/amd/mnt/gcc_torture_tests/logs/'+STAGING_BUILD+'/'+test_name+'/'+gcc_or_clang+'_'+STAGING_BUILD+'.log mail file://idcfs001/perfcompilefs/gcc_torture_tests/reports/'+STAGING_BUILD+'_vs_'+STAGING_BUILD_PRE+'/'+test_name+'/Report.html > $WORKSPACE/Report.html')
#################################################################################################################################################################################################################
