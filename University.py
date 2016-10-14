"""
学校列表包括学校基本信息，官方微博，招办微博 (来源新浪)
URL: http://kaoshi.edu.sina.com.cn/college/collegelist/view?provid=&typeid=&pro=&tab=&page=1

学校网站，地址，联系电话等，学校分数线，专业分数线 (来源ipin.com)
URL: http://www.ipin.com/school/schoolFilter.do

"""
import re
import requests
import lxml.html
from bson.objectid import ObjectId
from pymongo import MongoClient
from spider.Utils import fake_useragent

PROVINCE = {
    "1": "北京",
    "2": "天津",
    "3": "上海",
    "4": "重庆",
    "5": "河北",
    "6": "河南",
    "7": "山东",
    "8": "山西",
    "9": "安徽",
    "10": "江西",
    "11": "江苏",
    "12": "浙江",
    "13": "湖北",
    "14": "湖南",
    "15": "广东",
    "16": "广西",
    "17": "云南",
    "18": "贵州",
    "19": "四川",
    "20": "陕西",
    "21": "青海",
    "22": "宁夏",
    "23": "黑龙江",
    "24": "吉林",
    "25": "辽宁",
    "26": "西藏",
    "27": "新疆",
    "28": "内蒙古",
    "29": "海南",
    "30": "福建",
    "31": "甘肃",
    "32": "港澳台",
}


class UniversitySpiderSina(object):
    def __init__(self):
        self.tracker = open("univ.txt", 'w')
        self.url_template = "http://kaoshi.edu.sina.com.cn/college/collegelist/view?provid=&typeid=&pro=&tab=&page={}"

        conn = MongoClient("192.168.86.86:27017")
        conn.service.authenticate('serviceadmin', 'hello', mechanism='SCRAM-SHA-1')
        db = conn["service"]
        self.collection = db.university

    def crawl(self, start, end):
        for p in range(start, end + 1):
            headers = {
                "User-Agent": fake_useragent()
            }
            browser = requests.get(self.url_template.format(p), headers=headers)
            browser.encoding = "utf-8"
            if browser.status_code == 200:
                html = lxml.html.fromstring(browser.text)
                lis = html.xpath('//ul[@class="tabsContainer_ul"]/li')

                # Universities of current page
                for li in lis:
                    # University url like:
                    # http://kaoshi.edu.sina.com.cn/college/c/10001.shtml
                    url = li.xpath('./a')[0].attrib["href"]

                    # Extract university id from url
                    match = re.findall(r'/(\d+)\.shtml', url)
                    uid = int(match[0]) if match else 0

                    divs = li.xpath('.//div[@class="clearfix"]')

                    # Extract name, weibo
                    links = divs[0].xpath('.//a')
                    name = links[0].text_content().strip()
                    num = len(links)
                    weibo_official = "-"
                    weibo_enrollment_office = "-"
                    for n in range(1, num):
                        text = links[n].text_content().strip()
                        if text == "官方微博":
                            weibo_official = links[n].attrib["href"]

                        if text == "招办微博":
                            weibo_enrollment_office = links[n].attrib["href"]

                    # Extract info
                    ps = divs[1].xpath('.//p')
                    location = ps[0].text_content().strip().split(':')[1].strip()
                    utype = ps[2].text_content().strip().split(':')[1].strip()
                    subject_to = ps[4].text_content().strip().split(':')[1].strip()

                    tmp = re.findall(r'(\d+)', ps[1].text_content().strip())
                    key_discipline = "-" if len(tmp) == 0 else tmp[0]

                    tmp = re.findall(r'(\d+)', ps[3].text_content().strip())
                    master = "-" if len(tmp) == 0 else tmp[0]

                    tmp = re.findall(r'(\d+)', ps[5].text_content().strip())
                    doctor = "-" if len(tmp) == 0 else tmp[0]

                    # Extract tags
                    tags = []
                    spans = divs[2].xpath('.//span')
                    for span in spans:
                        tags.append(span.text_content().strip())

                    doc = {
                        "uid": uid,  # 学校ID
                        "name": name,  # 学校名称
                        "weibo_official": weibo_official,  # 官方微博
                        "weibo_enrollment_office": weibo_enrollment_office,  # 招办微博
                        "location": location,  # 所在地
                        "utype": utype,  # 类别
                        "subject_to": subject_to,  # 隶属
                        "key_discipline": key_discipline,  # 重点学科
                        "master": master,  # 硕士点数
                        "doctor": doctor,  # 博士点数
                        "tags": tags,  # 标签
                        "url": url,  # 第二次抓取用url
                    }
                    self.collection.insert_one(doc)

                print("Page{:>6}: [done]".format(p))
                print("Page{:>6}: [done]".format(p), file=self.tracker)
            else:
                print("Page{:>6}: [fail]".format(p))
                print("Page{:>6}: [fail]".format(p), file=self.tracker)

        self.tracker.cloes()


class UniversitySpiderIpin(object):
    def __init__(self):
        self.url = "http://www.ipin.com/school/filter/schoolList.do?searchKey=&score=false&level=%E6%9C%AC%E7%A7%91&&page=1"
        # score: true 返回的url为分数页面, false为学校详情页面
        # level: 本科/专科, url编码
        # page: 页数，目前为57页

    def crawl_info(self):

        # browser = requests.get(self.url)
        f = open("demo.txt", 'r')

        text = f.read()
        pattern = re.compile(r'<div.*</div>', re.DOTALL | re.MULTILINE)
        m = pattern.search(text)
        if m:
            print(m.group())

    def crawl_score(self):
        pass


if __name__ == "__main__":
    # univ = UniversitySpiderSina()
    # univ.crawl(1, 241)

    univ = UniversitySpiderIpin()
    univ.crawl_info()