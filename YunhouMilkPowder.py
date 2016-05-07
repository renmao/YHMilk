#coding=utf-8
__author__ = 'renmao'

import urllib2,re,os,datetime,json
from selenium import webdriver
from selenium.webdriver.support.ui import WebDriverWait

class Spider:
	#初始化
	def __init__(self):
		cap = webdriver.DesiredCapabilities.PHANTOMJS
		cap["phantomjs.page.settings.resourceTimeout"] = 10000
		#cap["phantomjs.page.settings.loadImages"] = False
		#cap["phantomjs.page.settings.localToRemoteUrlAccessEnabled"] = True
		self.driver = webdriver.PhantomJS(desired_capabilities=cap)
		self.index = 1
		self.fileName = 'YunhouMilkPowder.txt'
		self.errorUrl = []
		self.begin_time = datetime.datetime.now()
	#开始程序
	def start(self, maxPage):
		#创建要保存信息的文件
		file_object = open(self.fileName, 'w')
		file_object.write("")
		file_object.close()
		print "start the spider!"	
		for index in range(1,maxPage+1):
			self.loadListPage(index)
		#self.getError();
		self.printTime();
	#打开商品列表的页面
	def loadListPage(self, page):
		url = "http://list.yunhou.com/hs_0-so_desc-sf_default-fc_95740036_95740037-i_1-ps_48.html?p=" + str(page);
		result = '';
		try:
			request = urllib2.Request(url);#发起请求，回去静态网页
			response = urllib2.urlopen(request);
			content = response.read().decode("utf-8");#将获取的网页解码
			print "open the page", url
			#pattern = re.compile('<li class="shown".*?<a href="(,*?)" tar.*?goods-img">', re.S)
			pattern = re.compile('<li class="shown".*?href="(.*?)" targ.*?k">', re.S);#使用正则表达式匹配url信息
			items = re.findall(pattern,content)
			pattern = re.compile('<div class="col-cnt clearfix.*?href="(.*?)".*?ods-img">', re.S);
			items = items + re.findall(pattern, content);
			
			print "items.length", len(items)
			i = 0
			goodUrls = "";#遍历获取的商品url，打开每个url获取具体的信息
			for item in items:
				goodUrl = "http:" + item
				goodUrls += goodUrl + "\n"
				i += 1
				print "page",page, "i:", i,"length:", len(items)			
				self.loadGoodPage(goodUrl)#打开具体的商品网页
			#self.writeUrls(goodUrls)
			#self.loadGoodPage("http:" + items[0])
		except urllib2.URLError, e:#获取网页错误的异常处理
			if hasattr(e, "code"):
				print e.code
			if hasattr(e, "reason"):
				print e.reason
		except Exception,e:
			print e
	#将获取到的url写入文件
	def writeUrls(self, urls):
		try:
			file_object = open("yunhouMilkPowderUrls.txt", 'a')
			file_object.write(urlss)
			file_object.close()	
		except Exception,e:
			print e
	#打开具体的商品网页，获取具体的商品信息
	def loadGoodPage(self, url):
		print url
		info = {}
		try:
			wait = WebDriverWait(self.driver, 10)
			self.driver.get(url)
			
			#url
			info["url"] = url;
			
			#价格
			wait.until(lambda the_driver: the_driver.find_element_by_xpath("//*[@class='jFirstPrice']"))				
			price = self.driver.find_element_by_xpath("//*[@class='jFirstPrice']").get_attribute('textContent').strip()
			info["price"] = price
			
			#商品概要		
			title = self.driver.find_element_by_id('jGoodsH1').get_attribute('textContent').strip()
			info["title"] = title
			
			#商品介绍
			introduce = self.driver.find_element_by_class_name('goods-desc').get_attribute('textContent').strip()
			info["introduce"] = introduce
			
			#商品税费				
			tax = self.driver.find_element_by_id('jTariffInfo').get_attribute('textContent').strip()
			info["tax"] = tax
			
			#商铺				
			shop = self.driver.find_element_by_id('jShopName').get_attribute('textContent').strip()
			info["shop"] = shop
			
			#快递				
			post = self.driver.find_element_by_xpath("//*[@class='shop-tips f-l']").get_attribute('textContent').strip()
			info["post"] = post
			
			#图片信息
			imgTags = self.driver.find_elements_by_xpath('//div[@class="pic-list clearfix"]/a/img')
			imgs = [];
			for img in imgTags:			
				imgs.append(img.get_attribute("src"))
			info["imgs"] = imgs
			
			#评价数
			info["commentsTotal"] = "commentsTotal is missed!"
			wait.until(lambda the_driver: the_driver.find_element_by_id('jBtnCmdList'))				
			commentsTotal = self.driver.find_element_by_id('jBtnCmdList').get_attribute('textContent').strip()
			info["commentsTotal"] = commentsTotal
			
			#商品选项
			info["choice"] = "choice is missed!"	
			wait.until(lambda the_driver: the_driver.find_element_by_class_name('cur'))				
			choice = self.driver.find_element_by_class_name('cur').get_attribute('textContent').strip()
			info["choice"] = choice		
			
			#信息汇总
			result = json.dumps(info, ensure_ascii=False,indent=4).encode("utf8")
			print result
			#保存到文件
			file_object = open(self.fileName, 'a')
			file_object.write(result + "\n")
			file_object.close()			
			print "write the file"
		except Exception,e:#异常处理
			print "get info error ",e
			#self.errorUrl.append(url)
			result = json.dumps(info, ensure_ascii=False,indent=4).encode("utf8")
			print result
			file_object = open(self.fileName, 'a')
			file_object.write(result + "\n")
			file_object.close()			
			print "write the file"
	#重新打开出现问题的网页，获取信息
	def getError(self):
		print "getError:",self.index
		print "len(self.errorUrl)", len(self.errorUrl)
		if len(self.errorUrl) < 20:
			self.printTime()
			return
		self.index = self.index + 1
		errorUrls = self.errorUrl
		self.errorUrl = []
		i = 0;
		for url in errorUrls:
			i = i + 1	
			print len(errorUrls), i	
			self.loadGoodPage(url)
		self.getError()
	#显示程序运行时间
	def printTime(self):
		end_time = datetime.datetime.now()
		speed_time = self.begin_time - end_time
		print str(speed_time)

#主程序
spider = Spider()
spider.start(9);
