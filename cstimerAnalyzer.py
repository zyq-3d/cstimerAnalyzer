# -*- coding: utf-8 -*- #

# ------------------------------------------------------------------
# File Name: cstimerAnalyzer
# Author: Zhu Yunqi
# Version: ver0_1_1
# Created: 2024/02/04
# Description: Main Function: 读取cstimer成绩信息并与WCA成绩比较做出分析：平均成绩曲线、五次滑动平均曲线、五次平均曲线以及pb率

import matplotlib.pyplot as plt
from matplotlib import rc
import os
from decimal import Decimal, ROUND_HALF_UP
import csv

rc("font",family='MicroSoft YaHei',weight="bold")

TXT_DEST = 'rawTXTs'
RES_DEST = 'results'
EVENTS = ['333', '222', '444', '555', '666', '777', 'oh', 'bld', 'sk', 'py', 'sq', 'clk', 'minx', '444bld', '555bld']

def loadWCA():
	''' 读取WCA成绩

	return WCA: float 读取到的wca成绩
	'''
	wca = {}
	with open('WCA.csv', 'r') as f:
		rows = csv.reader(f)
		for i, row in enumerate(rows):
			if i == 0: continue # 第一行是表属性名
			wca[row[0]] = [float(x) for x in row[1:]] # {event: [average, single]}
			print('record for %s: %ss (Average), %ss (Single)'% (row[0], row[1], row[2]))
	
	return wca

def line2time(lines):
	''' 将文件中内容转换成成绩列表

	param lines: list[str]: txt中每行的内容
	return times: list[float]: 成绩列表
	'''
	times = []
	for line in lines:
		if '.' in line:
			time = line.split(' ')[1]
			if 'DNF' in time:
				time = float('inf')
			else: # 判断有无+2，是否有分钟

				if ':' in time: # 有分钟
					minutes, seconds = time.split(':')
					time = int(minutes) * 60
					if seconds[-1] == '+': # 有+2
						time += 2 + float(seconds[:-1])
					else: # 无+2
						time += float(seconds)

				else: # 无分钟
					if time[-1] == '+': # 有+2
						time = 2 + float(time[:-1])
					else: # 无+2
						time = float(time)

			times.append(time)
	return times

def AO5(Data):
	''' 计算去头尾AO5

	param Data: list 五次成绩
	return: float 保留两位小数的结果
	'''
	data = Data.copy()
	data.sort()  
	trimmed_data = data[1:-1]  # 去掉最高值和最低值 
	mean_result = sum(trimmed_data) / 3 
	if mean_result == float('inf'): return mean_result
	return float(Decimal(mean_result).quantize(Decimal('0.00'), rounding=ROUND_HALF_UP))  

def MAVG(times):
	''' 返回滑动平均（这部分有大量优化空间，但是数据有限所以没优化）

	param times: list 时间队列
	return movingAVG: list 滑动平均序列
	return validAVG: list 五次平均序列（初始需要为5的倍数加一
	'''
	movingAVG = []
	validAVG = []
	timeWindow = times[:5]
	average5 = AO5(timeWindow)
	movingAVG.append(average5)
	validAVG.append(average5)
	for i in range(5, len(times)):
		timeWindow = timeWindow[1:]
		timeWindow.append(times[i])
		average5 = AO5(timeWindow)
		movingAVG.append(average5)
		if (i + 1) % 5 == 0:
			validAVG.append(average5)
	return movingAVG, validAVG

def draw(times, movingAVG, validAVG, file):
	''' 画图

	param times: list 单次时间序列
	param movingAVG: list 滑动平均序列
	param validAVG: list 五次平均序列
	param file: str txt文件名字
	'''

	###### 单次成绩&滑动五次平均序列
	wca_avg, wca_single = WCA[EVENT]
	fig = plt.figure(figsize=(13, 6))
	plt.subplot(1,2,1)
	plt.plot(times, label='单次成绩')  
	plt.plot(range(5, len(times) + 1), movingAVG, label='滑动Ao5')
	# 添加平均成绩水平虚线  
	plt.axhline(y=wca_avg, color='r', linestyle='--', label='WCA Ao5: %s' %wca_avg)  
	# 添加单次成绩水平虚线  
	plt.axhline(y=wca_single, color='g', linestyle='--', label='WCA single: %s' %wca_single)  
	# 添加图例  
	plt.legend()  
	# 添加标题和坐标轴标签  
	betterRate_avg = sum([x < wca_avg for x in movingAVG]) / len(movingAVG)
	betterRate_single = sum([x < wca_single for x in times]) / len(times)
	plt.title('单次成绩&滑动Ao5走向图, 平均优官方率: {:.2%}, 单次优官方率: {:.2%}'.format(betterRate_avg, betterRate_single))  
	plt.xlabel('还原次数')  
	plt.ylabel('秒')  

	###### 五次平均序列
	plt.subplot(1,2,2)
	plt.plot(validAVG, label='Ao5')
	# 添加水平虚线  
	plt.axhline(y=wca_avg, color='r', linestyle='--', label='WCA Ao5: %s' %wca_avg)
	# 添加图例  
	plt.legend()  
	# 添加标题和坐标轴标签  
	betterRate = sum([x < wca_avg for x in validAVG]) / len(validAVG)
	plt.title('Ao5走向图，平均优官方率: {:.2%}'.format(betterRate))  
	plt.xlabel('Ao5次数')  
	plt.ylabel('秒')  
	plt.show()
	fig.savefig('%s.png' % os.path.join(RES_DEST, EVENT, file.split('.')[0]))

def analyze(file):
	''' 分析成绩文件，并将文件移动至rawTXTs
	
	param file: str, 待分析的txt文件路径
	'''
	with open(file, 'r', encoding='utf-8') as f:
		lines = f.read().split('\n')

	times = line2time(lines) # 获取时间列表
	movingAVG, validAVG = MAVG(times) # 获取滑动时间列表
	draw(times, movingAVG, validAVG, file)
	os.rename(file, os.path.join(TXT_DEST, EVENT, file))

def checkDir(file):
	''' 检查是否有需要的文件夹，若无则生成

	param file: str 待检查的路径
	'''
	try: # 检查results文件夹是否生成
	    os.makedirs(file, exist_ok=True)  
	except FileExistsError:  
	    pass  


if __name__ == '__main__':
	files = os.listdir('./')
	checkDir(TXT_DEST)
	checkDir(RES_DEST)
	EVENT = input('请选择练习的项目(' + ', '.join(EVENTS) + '): ')
	if EVENT not in EVENTS:
		print('项目名称错误！')
		exit()
	checkDir(TXT_DEST+ '/' + EVENT)
	checkDir(RES_DEST + '/' + EVENT)
	WCA = loadWCA()
	for file in files:
		if file.endswith('.txt') and file != 'WCA.txt' and file != 'requirements.txt':
			analyze(file)