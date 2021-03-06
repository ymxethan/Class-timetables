# coding: utf-8
#!/usr/bin/python

import sys
import time, datetime
import json
from random import Random
import importlib

checkFirstWeekDate = 0
checkReminder = 1

YES = 0
NO = 1

DONE_firstWeekDate = time.time()
DONE_reminder = ""
DONE_EventUID = ""
DONE_UnitUID = ""
DONE_CreatedTime = ""
DONE_ALARMUID = ""


sessionList = []
classInfoList = []

def main():
	basicSetting();
	uniteSetting();
	classInfoHandle();
	icsCreateAndSave();
	print("\nAll Done!\n")

def basicSetting():
	info = "欢迎使用课程表生成工具。\n接下来你需要设置一些基础的信息方便生成数据\n"
	print (info)
	
	info = "请设置第一周的星期一日期(如：20180903):\n"
	firstWeekDate = input(info)
	checkInput(checkFirstWeekDate, firstWeekDate)
	info = "正在配置上课时间信息……\n"
	print(info)
	try :
		setClassTime()
		print("配置上课时间信息完成。\n")
	except :
		sys_exit()

	info = "正在配置课堂信息……\n"
	print(info)
	try :
		setClassInfo()
		print("配置课堂信息完成。\n")
	except :
		sys_exit()

	info = "正在配置提醒功能，请输入数字选择提醒时间\n【0】不提醒\n【1】上课前 10 分钟提醒\n【2】上课前 30 分钟提醒\n【3】上课前 1 小时提醒\n【4】上课前 2 小时提醒\n【5】上课前 1 天提醒\n"
	reminder = input(info)
	checkInput(checkReminder, reminder)

def uniteSetting():
	global DONE_ALARMUID
	DONE_ALARMUID = random_str(30)
	global DONE_UnitUID
	DONE_UnitUID = random_str(20)
	print("uniteSetting")

def classInfoHandle():
	global classInfoList
	global DONE_firstWeekDate
	i = 0

	for classInfo in classInfoList :
		# 具体日期计算出来
		week = json.dumps(classInfo["week"])
		weekday = float(json.dumps(classInfo["weekday"]))
		
		dateLength = float((int(week) - 1) * 7)
		date = datetime.datetime.fromtimestamp(int(time.mktime(DONE_firstWeekDate))) + datetime.timedelta(days = dateLength + weekday - 1)
		string = date.strftime('%Y%m%d')

		dateList = []
		dateList.append(string)
		classInfo["date"] = dateList
		# 设置 UID
		global DONE_CreatedTime, DONE_EventUID
		CreateTime()
		classInfo["CREATED"] = DONE_CreatedTime
		classInfo["DTSTAMP"] = DONE_CreatedTime
		UID_List = []
		for date  in dateList:
			UID_List.append(UID_Create())
		classInfo["UID"] = UID_List
	print("classInfoHandle")

def icsCreateAndSave():
	icsString = "BEGIN:VCALENDAR\nMETHOD:PUBLISH\nVERSION:2.0\nX-WR-CALNAME:课程表\nX-APPLE-CALENDAR-COLOR:#FF2968\nX-WR-TIMEZONE:Asia/Shanghai\nCALSCALE:GREGORIAN\n"
	global sessionList, DONE_ALARMUID, DONE_UnitUID
	eventString = ""
	for classInfo in classInfoList:
		i = int(classInfo["session"]-1)
		className = classInfo["className"]
		endTime = sessionList[i]["endTime"]
		startTime = sessionList[i]["startTime"]
		index = 0
		for date in classInfo["date"]:
			eventString = eventString+"BEGIN:VEVENT\nTRANSP:OPAQUE\nCREATED:"+classInfo["CREATED"]
			eventString = eventString+"\nUID:"+classInfo["UID"][index]
			eventString = eventString+"\nDTEND;TZID=Asia/Shanghai:"+date+"T"+endTime
			eventString = eventString+"\nX-APPLE-TRAVEL-ADVISORY-BEHAVIOR:AUTOMATIC\nSUMMARY:"+className
			eventString = eventString+"\nDTSTART;TZID=Asia/Shanghai:"+date+"T"+startTime+"00"
			eventString = eventString+"\nDTSTAMP:"+DONE_CreatedTime
			eventString = eventString+"\nSEQUENCE:0\nBEGIN:VALARM\nX-WR-ALARMUID:"+DONE_ALARMUID
			eventString = eventString+"\nUID:"+DONE_UnitUID
			eventString = eventString+"\nTRIGGER:"+DONE_reminder
			eventString = eventString+"\nACTION:DISPLAY\nEND:VALARM\nEND:VEVENT\n"

			index += 1
	icsString = icsString + eventString + "END:VCALENDAR"
	save(icsString)
	print("icsCreateAndSave")

def UID_Create():
	return random_str(20)

def CreateTime():
	# 生成 CREATED
	global DONE_CreatedTime
	date = datetime.datetime.now().strftime("%Y%m%dT%H%M%S")
	DONE_CreatedTime = date + "Z"

def setClassTime():
	data = []
	with open('conf_classTime.json', 'r') as f:
		data = json.load(f)
	global sessionList
	sessionList = data["classTime"]
	print("setClassTime")
	
def setClassInfo():
	data = []
	with open('conf_classInfo_G1-7.json', 'r') as f:
		data = json.load(f)
	global classInfoList
	classInfoList = data["classInfo"]
	print("setClassInfo")

def setFirstWeekDate(firstWeekDate):
	global DONE_firstWeekDate
	DONE_firstWeekDate = time.strptime(firstWeekDate,'%Y%m%d')

def setReminder(reminder):
	global DONE_reminder
	reminderList = ["-PT10M","-PT30M","-PT1H","-PT2H","-P1D"]
	if(reminder == "1"):
		DONE_reminder = reminderList[0]
	elif(reminder == "2"):
		DONE_reminder = reminderList[1]
	elif(reminder == "3"):
		DONE_reminder = reminderList[2]
	elif(reminder == "4"):
		DONE_reminder = reminderList[3]
	elif(reminder == "5"):
		DONE_reminder = reminderList[4]
	else:
		DONE_reminder = "NULL"


	print("setReminder",reminder)

def checkReminder(reminder):
	print("checkReminder:",reminder)
	List = ["0","1","2","3","4","5"]
	for num in List:
		if (reminder == num):
			return YES
	return NO

def checkFirstWeekDate(firstWeekDate):
	# 长度判断
	if(len(firstWeekDate) != 8):
		return NO;
	
	year = firstWeekDate[0:4]
	month = firstWeekDate[4:6]
	date = firstWeekDate[6:8]
	dateList = [31,29,31,30,31,30,31,31,30,31,30,31]

	# 年份判断
	if(int(year) < 1970):
		return NO
	# 月份判断
	if(int(month) == 0 or int(month) > 12):
		return NO;
	# 日期判断
	if(int(date) > dateList[int(month)-1]):
		return NO;

	print("checkFirstWeekDate:",firstWeekDate)
	return YES

def checkInput(checkType, input):
	if(checkType == checkFirstWeekDate):
		if (checkFirstWeekDate(input)):
			info = "输入有误，请重新输入第一周的星期一日期(如：20160905):\n"
			firstWeekDate = input(info)
			checkInput(checkFirstWeekDate, firstWeekDate)
		else:
			setFirstWeekDate(input)
	elif(checkType == checkReminder):
		if(checkReminder(input)):
			info = "输入有误，请重新输入\n【1】上课前 10 分钟提醒\n【2】上课前 30 分钟提醒\n【3】上课前 1 小时提醒\n【4】上课前 2 小时提醒\n【5】上课前 1 天提醒\n"
			reminder = input(info)
			checkInput(checkReminder, reminder)
		else:
			setReminder(input)

	else:
		print("程序出错了……")
		end

def random_str(randomlength):
    strs = ''
    chars = 'AaBbCcDdEeFfGgHhIiJjKkLlMmNnOoPpQqRrSsTtUuVvWwXxYyZz0123456789'
    length = len(chars) - 1
    random = Random()
    for i in range(randomlength):
        strs+=chars[random.randint(0, length)]
    return strs


def save(string):
     f = open("class.ics", 'wb')
     f.write(string.encode("utf-8"))
     f.close()

def sys_exit():
	print("配置文件错误，请检查。\n")
	sys.exit()
	
importlib.reload(sys)
main()
