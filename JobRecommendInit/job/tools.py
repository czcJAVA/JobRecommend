# -*- coding: utf-8 -*-
# @Time: 2023-1-29 9:01
# @File: tools.py
# @IDE: PyCharm

import time
from lxml import etree
from multiprocessing.dummy import Pool
import pymysql

import os
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options

# 获取当前文件的目录
current_dir = os.path.dirname(os.path.abspath(__file__))
# 指定 chromedriver 的路径
driver_path = os.path.join(current_dir, 'chromedriver.exe')  # 确保 chromedriver 文件名是正确的


# city, all_page, spider_code
def lieSpider(key_word, city, all_page):
    # print(key_word, city, all_page, 123)
    city_dict = {'全国': '410', '北京': '010', '上海': '020', '天津': '030', '重庆': '040', '广州': '050020',
                 '深圳': '050090',
                 '苏州': '060080', '南京': '060020', '杭州': '070020', '大连': '210040', '成都': '280020',
                 '武汉': '170020',
                 '西安': '270020'}
    # print(key_word, all_page, city_dict[city])
    urls_list = get_urls(key_word, all_page, city_dict[city])
    # print(urls_list)
    pool = Pool(1)  # 线程池对象，速度过快封IP，只能开两个线程
    pool.map(get_pages, urls_list)
    return 0


def get_urls(key_word, all_page, city_code):
    """此函数用来生成需要爬取的数据的URL"""
    urls_list = []
    for i in range(0, int(all_page)):
        url = 'https://www.liepin.com/zhaopin/?city={}&dq={}&currentPage={}&pageSize=40&key={}'.format(city_code,
                                                                                                       city_code, i,
                                                                                                       key_word)
        urls_list.append(url)
    return urls_list


def get_city():
    """此函数用来抓取城市对应的code用来请求各个城市的职位信息"""
    print('开始抓取城市列表...')

    chrome_options = Options()
    chrome_options.add_argument('--headless')  # 运行在无头模式
    # 使用 Service 指定 chromedriver 路径
    service = Service(driver_path)
    driver = webdriver.Chrome(service=service, options=chrome_options)

    # chrome_options = Options()
    # chrome_options.add_argument('--headless')
    # driver = webdriver.Chrome(options=chrome_options)

    # option = webdriver.ChromeOptions()  # 初始化一个浏览器对象
    # prefs = {'profile.managed_default_content_settings.images': 2}  # 设置不显示网页以提高抓取效率图片
    # option.add_experimental_option('excludeSwitches', ['enable-automation'])  # 设置去除自动化提示
    # option.add_experimental_option("detach", True)
    # option.add_experimental_option('prefs', prefs)
    # driver = webdriver.Chrome(options=option)  # 创建一个浏览器实例

    city_url = 'https://www.liepin.com/zhaopin/?inputFrom=head_navigation&scene=init&workYearCode=0&ckId=ayvlgrooqq8e4w2b3yoae69sd91dmbq9'  # 搜索页地址
    driver.get(city_url)  # 请求搜索页地址，抓取城市对应的code
    time.sleep(3)  # 等待3秒
    req_html = etree.HTML(driver.page_source)  # 把页面源码变成xpath对象
    code_list = req_html.xpath('//li[@data-key="dq"]/@data-code')
    name_list = req_html.xpath('//li[@data-key="dq"]/@data-name')
    city_list = [[name_list[x], code_list[x]] for x in range(len(name_list))]
    print('抓取到的城市列表:', city_list)
    return city_list


def get_pages(url):
    """此函数用来爬取页面职位信息"""
    mysql_conn = get_mysql()  # 连接数据库
    conn = mysql_conn[0]  # 获取数据库
    cur = mysql_conn[1]  # 获取游标
    print('开始爬取 {}...'.format(url))

    chrome_options = Options()
    chrome_options.add_argument('--headless')  # 运行在无头模式
    # 使用 Service 指定 chromedriver 路径
    service = Service(driver_path)
    driver = webdriver.Chrome(service=service, options=chrome_options)

    # chrome_options = Options()
    # # chrome_options.add_argument('--headless')  # 注释掉这一行，以显示浏览器界面
    #
    # driver = webdriver.Chrome(options=chrome_options)

    # option = webdriver.ChromeOptions()
    # prefs = {'profile.managed_default_content_settings.images': 2}
    # option.add_experimental_option('excludeSwitches', ['enable-automation'])
    # option.add_experimental_option("detach", True)
    # option.add_experimental_option('prefs', prefs)
    # driver = webdriver.Chrome(options=option)

    driver.get(url)
    time.sleep(3)
    req_html = etree.HTML(driver.page_source)
    # print(req_html)
    job = req_html
    name = job.xpath('//div[@class="jsx-2387891236 ellipsis-1"]/text()')
    salary = job.xpath('//span[@class="jsx-2387891236 job-salary"]/text()')
    address = job.xpath('//span[@class="jsx-2387891236 ellipsis-1"]/text()')
    education = job.xpath('//div[@class="jsx-2387891236 job-labels-box"]/span[2]/text()')
    experience = job.xpath('//div[@class="jsx-2387891236 job-labels-box"]/span[1]/text()')
    com_name = job.xpath('//span[@class="jsx-2387891236 company-name ellipsis-1"]/text()')
    tag_list = job.xpath('//div[@class="jsx-2387891236 company-tags-box ellipsis-1"]')
    label_list = []
    scale_list = []
    for tag in tag_list:
        span_list = tag.xpath('./span/text()')
        label_list.append(span_list[0])
        scale_list.append(span_list[-1])
    href_list = job.xpath('//a[@data-nick="job-detail-job-info"]/@href')
    href_list = [x.split('?')[0] for x in href_list]
    if len(name) == len(salary) == len(address) == len(education) == len(experience) == len(com_name) == len(
            label_list) == len(scale_list) == len(href_list):
        for i in range(0, len(name)):
            select_sql = '''SELECT href FROM job_data'''
            cur.execute(select_sql)
            href_list_mysql = cur.fetchall()
            href_list_mysql = [x[0] for x in href_list_mysql]
            # print(href_list_mysql)
            if href_list[i] not in href_list_mysql:
                insert_sql = '''INSERT INTO job_data(name,salary,place,education,experience,company,label,scale,href,key_word) VALUES (%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)'''
                list_1 = [name[i], salary[i], address[i], education[i], experience[i], com_name[i], label_list[i],
                          scale_list[i], href_list[i], url.split('=')[-1]]
                print(list_1)
                try:
                    cur.execute(insert_sql, list_1)
                except Exception as e:
                    print(e)
                    conn.rollback()  # 执行失败后回滚数据库
    else:
        print('爬取数据有误，开始下一页...')
    time.sleep(3)
    cur.close()
    conn.close()
    driver.quit()


def get_mysql():
    """此函数用来连接数据库"""
    conn = pymysql.connect(host='localhost',  # 数据库地址
                           port=3306,  # 端口
                           user='root',  # 用户名
                           passwd='123456',  # 密码
                           database='recommend_job',  # 数据库名称
                           autocommit=True,  # 自动提交
                           charset='utf8mb4')  # 编码方式
    cur = conn.cursor()  # 获取游标
    return conn, cur  # 返回数据库和游标


if __name__ == '__main__':
    lieSpider('java', '北京', '1')
