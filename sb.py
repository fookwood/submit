#!/usr/bin/python

import urllib, httplib
import os, sys, re, time


username = {"zoj":"woodfook","poj":"fkfkfk","hdu":"fkfkfk"}
password = {"zoj":"123"     ,"poj":"fkfkfk","hdu":"fkfkfk"}
oj = None
problemid = None
sourcefile = None
sourcecode = None
lang = "c++"
host = {"zoj":"acm.zju.edu.cn", 
		"poj":"poj.org",
		"hdu":"acm.hdu.edu.cn" }
# Host of each Online Judge

def prearg():
	global oj,problemid,sourcecode,sourcefile
	if len(sys.argv) < 4 :
		D("Usage: sb OJname Problemid Sourcefile\n")
	oj = sys.argv[1].lower()
	if oj == "zoj" or oj == "zju":
		oj = "zoj"
	elif oj == "poj" or oj == "pku":
		oj = "poj"
	elif oj == "hdu" or oj == "hdoj":
		oj = "hdu"
	else:
		D("I now don't support "+oj+"\n")
	problemid = sys.argv[2]
	sourcefile = sys.argv[3]
	if os.path.exists(sourcefile) == False:
		D("I can't find file : "+sourcefile+"\n")
	f = open(sourcefile)
	sourcecode = f.read()
	f.close()

def request(method,path,body="",headers={}):
	global oj
	conn = httplib.HTTPConnection(host[oj]);
#	conn.set_debuglevel(1)
	conn.request(method,path,body,headers)
	rst = conn.getresponse()
	strr = rst.read()
	conn.close()
	return {"response":rst,"string":strr}

def D(strr):
	"""some thing wrong, output strr and exit
	"""
	sys.stderr.write(strr)
	sys.exit(1)

def getlanguage(code):
	l = code.split(".")
	if len(l) == 1:
		return None
	l = l[-1]
	if l == "cpp" or l == "hpp" or l == "cxx":
		return "c++"
	if l == "c":
		return "c"
	if l == "java":
		return l
	if l == "pas":
		return "pascal"
	if l == "php":
		return l
	if l.startwith("f") or l.startwith("F"):
		return "fortran"
	if l == "py" :
	 	return "python"
	if l == "pl" :
	 	return "perl"

def getcookie():
	"""simulate 'POST' to get cookies
	"""
	params = None
	path = None
	if oj == "zoj":
		params = { "handle":username[oj], "password":password[oj]}
		path = "/onlinejudge/login.do"
	if oj == "poj":
		params = {"user_id1":username[oj],"password1":password[oj],"B1":"login","url":"/"}
		path = "/login"
	if oj == "hdu":
		params = {"username":username[oj],"userpass":password[oj],"login":"Sign In"}
		path = "/userloginex.php?action=login"
	
	params = urllib.urlencode( params )
	header = {"Content-Type":"application/x-www-form-urlencoded",
			   "Content-Length":str( len(params) ) } 
	rst=request("POST",path,params,header)["response"]
	if rst.status == httplib.OK:
		D("Is your username && password all right?\n")
	strr = rst.getheader("Set-Cookie").split(" ");
	if oj == "zoj":
		return strr[2]
	return strr[0]

def submitpoj( problemid, lang, code ):
	params = urllib.urlencode( {"problem_id":problemid,
								"language":1,
								"source":code } )
	header = {"Cookie":getcookie(),
	          "Content-Type":"application/x-www-form-urlencoded",
	          "Content-Length":str(len(params))}
	rst = request("POST","/submit",params,header)["response"]
	if rst.status == httplib.OK:
		D("You may check your problemid and code length...\n")
	status = ""
	while status == "Waiting" or status == "Compiling" or status == "Running & Judging" or status == "":
		strr = request("GET","/status?user_id="+username[oj])["string"].split("\n")[2]
		temp = strr[strr.find("font"):].split("<")[0].split(">")[1]
		if temp != status:
			print temp
		status = temp
		time.sleep(1)

def submitzoj( problemid, lang, code ):
	path = "/onlinejudge/showProblem.do?problemCode=";
	header = {"Cookie":getcookie() }
	temp = request("GET",path+problemid,headers=header)
	if temp["response"].status != httplib.OK:
		D("Can't get zoj problemn\n")
	strr= temp["string"]
	if strr.find("No such problem") != -1:
		D("No such problem : "+problemid+"\n")
	problemid = ""
	i = 0
	strr = strr[ strr.find("problemId=")+10: ]
	while strr[i].isdigit():
		problemid += strr[i]
		i = i+1

	params = urllib.urlencode({"problemId":problemid,
							   "languageId":1,
							   "source":code})
	header["Content-Type"]="application/x-www-form-urlencoded"
	header["Content-Length"]=str( len(params) ) 
	temp = request("POST","/onlinejudge/submit.do",params,header)
	strr = temp["string"][ temp["string"].find("red'>")+5: ]
	statusid = ""
	i = 0
	while strr[i].isdigit():
		statusid += strr[i]
		i = i+1

	path = "/onlinejudge/showRuns.do?contestId=1&search=true&"
	path += "idStart="+statusid+"&idEnd="+statusid
	status = "Compiling"
	while status == "Compiling" or status == "Running":
		temp = request("GET",path)["string"].split("\n")[281].strip()
		if temp != status:
			print temp
		status =  temp
		time.sleep(1)

def submithdu( problemid, lang, code ):
	params = urllib.urlencode( {"problemid":problemid,
								"language":1,
								"usercode":code,
								"check":0} )
	header = {"Cookie":getcookie(),
	          "Content-Type":"application/x-www-form-urlencoded",
	          "Content-Length":str(len(params))}
	rst = request("POST","/submit.php?action=submit",params,header)["response"]
	if rst.status == httplib.OK:
		D("You may check your problemid and code length...\n")
	status = ""
	while status == "Queuing" or status == "":
		strr = request("GET","/status.php?user="+username[oj])["string"].split("\n")[78]
		temp = strr[strr.find("font color"):].split("<")[0].split(">")[1]
		if temp != status:
			print temp
		status = temp
		time.sleep(1)


# connect to server, login, submit code
if __name__ == "__main__":
	prearg()
	if oj == "zoj":
		submitzoj(problemid,lang,sourcecode)
	elif oj == "poj":
		submitpoj(problemid,lang,sourcecode)
	else:
		submithdu(problemid,lang,sourcecode)
