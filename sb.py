#!/usr/bin/python

import urllib, httplib
import os, sys, re, time


username = "woodfook"
password = "123"
oj = None
problemid = None
sourcefile = None
lang = "c++"
host = {"zoj":"acm.zju.edu.cn", 
		"poj":"poj.org",
		"hdu":"acm.hdu.edu.cn" }
	
# Host of each Online Judge
def prearg():
	global oj,problemid,sourcefile
	if len(sys.argv) < 4 :
		D("Lack of parameters\n")
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
	sourcefile = f.read()
	f.close()

def request(method,path,body="",headers={}):
	global oj
	conn = httplib.HTTPConnection(host[oj]);
#conn.set_debuglevel(1)
	conn.request(method,path,body,headers)
	rst = conn.getresponse()
	strr = rst.read()
	conn.close()
	return {"response":rst,"string":strr}

def D(strr):
	"""some thing wrong, output strr and exit
	"""
	sys.stdout.write(strr)
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

def readfile(code):
	"""return source code in source file
	"""
	f = open(code,"r")
	text = f.read()
	f.close()
	return text;

def getcookiezoj():
	"""simulate 'POST' to get cookies
	"""
	params = { "handle":username, "password":password }
	params = urllib.urlencode( params )
	header = {"Content-Type":"application/x-www-form-urlencoded",
			   "Content-Length":str( len(params) ) } 
	rst=request("POST","/onlinejudge/login.do",params,header)["response"]
	if rst.status == httplib.OK:
		D("Is your username && password all right?\n")
	strr = rst.getheader("Set-Cookie").split(" ");
	return strr[2]

def submitzoj( problemid, lang, code ):
	path = "/onlinejudge/showProblem.do?problemCode=";
	header = {"Cookie":getcookiezoj()+" last_language=1" }
	temp = request("GET",path+problemid,headers=header)
	rst = temp["response"]
	strr= temp["string"]
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
		time.sleep(1)
		status = request("GET",path)["string"].split("\n")[281].strip()

	print status
	return
	if rst.status != httplib.OK:
		D("Can't get zoj problemn\n")
	if rst.read().find("No Such Problem") != -1:
		D("No such problem : "+problemid+"\n")
	


# connect to server, login, submit code
if __name__ == "__main__":
	prearg()
	submitzoj(problemid,lang,sourcefile)	
