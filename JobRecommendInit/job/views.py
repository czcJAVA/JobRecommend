from django.shortcuts import render, redirect
from django.http import JsonResponse
# Create your views here.
from job import models
import re
from psutil import *
from numpy import *
from job import tools
from job import job_recommend

spider_code = 0  # 定义全局变量，用来识别爬虫的状态，0空闲，1繁忙


# python manage.py inspectdb > job/models.py
# 使用此命令可以将数据库表导入models生成数据模型


def login(request):
    if request.method == "POST":
        user = request.POST.get('user')
        pass_word = request.POST.get('password')
        print('user------>', user)
        users_list = list(models.UserList.objects.all().values("user_id"))
        users_id = [x['user_id'] for x in users_list]
        print(users_id)
        # print(students_num)
        ret = models.UserList.objects.filter(user_id=user, pass_word=pass_word)
        if user not in users_id:
            return JsonResponse({'code': 1, 'msg': '该账号不存在！'})
        elif ret:
            # 有此用户 -->> 跳转到首页
            # 登录成功后，将用户名和昵称保存到session 中，
            request.session['user_id'] = user
            user_obj = ret.last()

            if user_obj:  # 检查用户对象是否存在
                user_name = user_obj.user_name
                request.session['user_name'] = user_name
                return JsonResponse({'code': 0, 'msg': '登录成功！', 'user_name': user_name})
        else:
            return JsonResponse({'code': 1, 'msg': '密码错误！'})
    else:
        return render(request, "login.html")


def register(request):
    if request.method == "POST":
        user = request.POST.get('user')
        pass_word = request.POST.get('password')
        user_name = request.POST.get('user_name')
        users_list = list(models.UserList.objects.all().values("user_id"))
        users_id = [x['user_id'] for x in users_list]
        if user in users_id:
            return JsonResponse({'code': 1, 'msg': '该账号已存在！'})
        else:
            models.UserList.objects.create(user_id=user, user_name=user_name, pass_word=pass_word)
            request.session['user_id'] = user  # 设置缓存
            request.session['user_name'] = user_name
            return JsonResponse({'code': 0, 'msg': '注册成功！'})
    else:
        return render(request, "register.html")


# 退出(登出)
def logout(request):
    # 1. 将session中的用户名、昵称删除
    request.session.flush()
    # 2. 重定向到 登录界面
    return redirect('login')


def index(request):
    """此函数用于返回主页，主页包括头部，左侧菜单"""
    return render(request, "index.html")


def welcome(request):
    """此函数用于处理控制台页面"""
    job_data = models.JobData.objects.all().values()  # 查询所有的职位信息
    all_job = len(job_data)  # 职位信息总数
    list_1 = []  # 定义一个空列表
    for job in list(job_data):  # 使用循环处理最高哦薪资
        try:  # 使用try...except检验最高薪资的提取，如果提取不到则加入0
            salary_1 = float(re.findall(r'-(\d+)k', job['salary'])[0])  # 使用正则提取最高薪资
            job['salary_1'] = salary_1  # 添加一个最高薪资
            list_1.append(salary_1)  # 把最高薪资添加到list_1用来计算平均薪资
        except Exception as e:
            print(e)
            job['salary_1'] = 0
            list_1.append(0)
    job_data = sorted(list(job_data), key=lambda x: x['salary_1'], reverse=True)  # 反向排序所有职位信息的最高薪资
    # print(job_data)
    job_data_10 = job_data[0:10]  # 取最高薪资前10用来渲染top—10表格
    # print(job_data[0:10])
    job_data_1 = job_data[0]  # 取出最高薪资的职位信息
    mean_salary = int(mean(list_1))  # 计算平均薪资
    spider_info = models.SpiderInfo.objects.filter(spider_id=1).first()  # 查询爬虫程序运行的数据记录
    # print(spider_info)
    return render(request, "welcome.html", locals())


def spiders(request):
    global spider_code
    # print(spider_code)
    spider_code_1 = spider_code
    return render(request, "spiders.html", locals())


def start_spider(request):
    if request.method == "POST":
        key_word = request.POST.get("key_word")
        city = request.POST.get("city")
        page = request.POST.get("page")
        role = request.POST.get("role")
        spider_code = 1  # 改变爬虫状态
        spider_model = models.SpiderInfo.objects.filter(spider_id=1).first()
        # print(spider_model)
        spider_model.count += 1  # 给次数+1
        spider_model.page += int(page)  # 给爬取页数加上选择的页数
        spider_model.save()
        if role == '猎聘网':
            # print(key_word,city,page)
            spider_code = tools.lieSpider(key_word=key_word, city=city, all_page=page)
        return JsonResponse({"code": 0, "msg": "爬取完毕!"})
    else:
        return JsonResponse({"code": 1, "msg": "请使用POST请求"})


def job_list(request):
    return render(request, "job_list.html", locals())


def get_job_list(request):
    """此函数用来渲染职位信息列表"""
    page = int(request.GET.get("page", ""))  # 获取请求地址中页码
    limit = int(request.GET.get("limit", ""))  # 获取请求地址中的每页数据数量
    keyword = request.GET.get("keyword", "")
    price_min = request.GET.get("price_min", "")
    price_max = request.GET.get("price_max", "")
    edu = request.GET.get("edu", "")
    city = request.GET.get("city", "")
    job_data_list = list(models.JobData.objects.filter(name__icontains=keyword, education__icontains=edu,
                                                       place__icontains=city).values())  # 查询所有的职位信息
    job_data = []
    if price_min != "" or price_max != "":
        for job in job_data_list:
            try:
                salary_1 = '薪资' + job['salary']
                max_salary = float(re.findall(r'-(\d+)k', salary_1)[0])  # 使用正则提取最高薪资
                min_salary = float(re.findall(r'薪资(\d+)', salary_1)[0])  # 使用正则提取最低薪资
                if price_min == "" and price_max != "":
                    if max_salary <= float(price_max):
                        job_data.append(job)
                elif price_min != "" and price_max == "":
                    if min_salary >= float(price_min):
                        job_data.append(job)
                else:
                    if min_salary >= float(price_min) and float(price_max) >= max_salary:
                        job_data.append(job)
            except Exception as e:  # 如果筛选不出就跳过
                continue
    else:
        job_data = job_data_list
    job_data_1 = job_data[(page - 1) * limit:limit * page]
    for job in job_data_1:
        ret = models.SendList.objects.filter(user_id=request.session.get("user_id"), job_id=job['job_id']).values()
        if ret:
            job['send_key'] = 1
        else:
            job['send_key'] = 0
    # print(job_data_1)
    if len(job_data) == 0 or len(job_data_list) == 0:
        return JsonResponse({"code": 1, "msg": "没找到需要查询的数据！", "count": "{}".format(len(job_data)), "data": job_data_1})
    return JsonResponse({"code": 0, "msg": "success", "count": "{}".format(len(job_data)), "data": job_data_1})


def get_psutil(request):
    """此函数用于读取cpu使用率和内存占用率"""
    # cpu_percent()可以获取cpu的使用率，参数interval是获取的间隔
    # virtual_memory()[2]可以获取内存的使用率
    return JsonResponse({'cpu_data': cpu_percent(interval=1), 'memory_data': virtual_memory()[2]})


def get_pie(request):
    """此函数用于渲染控制台饼图的数据,要求学历的数据和薪资待遇的数据"""
    edu_list = ['博士', '硕士', '本科', '大专', '不限']
    edu_data = []
    for edu in edu_list:
        edu_count = len(models.JobData.objects.filter(education__icontains=edu))  # 使用for循环，查询字段education包含这些学历的职位信息
        edu_data.append({'name': edu, "value": edu_count})  # 添加到学历的数据列表中
    # print(edu_data)
    list_5 = []
    list_10 = []
    list_15 = []
    list_20 = []
    list_30 = []
    list_50 = []
    list_51 = []
    job_data = models.JobData.objects.all().values()  # 查询所有的职位信息
    for job in list(job_data):
        try:
            salary_1 = float(re.findall(r'-(\d+)k', job['salary'])[0])  # 提取薪资待遇的最高薪资要求
            if salary_1 <= 5:  # 小于5K则加入list_5
                list_5.append(salary_1)
            elif 10 >= salary_1 > 5:  # 在5K和10K之间，加入list_10
                list_10.append(salary_1)
            elif 15 >= salary_1 > 10:  # 10K-15K加入list_15
                list_15.append(salary_1)
            elif 20 >= salary_1 > 15:  # 15K-20K加入list_20
                list_20.append(salary_1)
            elif 30 >= salary_1 > 20:  # 20K-30K 加list_30
                list_30.append(salary_1)
            elif 50 >= salary_1 > 30:  # 30K-50K加入list_50
                list_50.append(salary_1)
            elif salary_1 > 50:  # 大于50K加入list_51
                list_51.append(salary_1)
        except Exception as e:
            job['salary_1'] = 0
    salary_data = [{'name': '5K及以下', 'value': len(list_5)},  # 生成薪资待遇各个阶段的数据字典，value是里面职位信息的数量
                   {'name': '5-10K', 'value': len(list_10)},
                   {'name': '10K-15K', 'value': len(list_15)},
                   {'name': '15K-20K', 'value': len(list_20)},
                   {'name': '20K-30K', 'value': len(list_30)},
                   {'name': '30-50K', 'value': len(list_50)},
                   {'name': '50K以上', 'value': len(list_51)}]
    # print(salary_data)
    return JsonResponse({'edu_data': edu_data, 'salary_data': salary_data})


def send_job(request):
    """此函数用于投递职位和取消投递"""
    if request.method == "POST":
        user_id = request.session.get("user_id")
        job_id = request.POST.get("job_id")
        send_key = request.POST.get("send_key")
        if int(send_key) == 1:
            models.SendList.objects.filter(user_id=user_id, job_id=job_id).delete()
        else:
            models.SendList.objects.create(user_id=user_id, job_id=job_id)
        return JsonResponse({"Code": 0, "msg": "操作成功"})


def job_expect(request):
    if request.method == "POST":
        job_name = request.POST.get("key_word")
        city = request.POST.get("city")
        ret = models.UserExpect.objects.filter(user=request.session.get("user_id"))
        # print(ret)
        if ret:
            ret.update(key_word=job_name, place=city)
        else:
            user_obj = models.UserList.objects.filter(user_id=request.session.get("user_id")).first()
            models.UserExpect.objects.create(user=user_obj, key_word=job_name, place=city)
        return JsonResponse({"Code": 0, "msg": "操作成功"})
    else:
        ret = models.UserExpect.objects.filter(user=request.session.get("user_id")).values()
        print(ret)
        if len(ret) != 0:
            keyword = ret[0]['key_word']
            place = ret[0]['place']
        else:
            keyword = ''
            place = ''
        return render(request, "expect.html", locals())


def get_recommend(request):
    recommend_list = job_recommend.recommend_by_item_id(request.session.get("user_id"), 9)
    print(recommend_list)
    return render(request, "recommend.html", locals())


def send_page(request):
    return render(request, "send_list.html")


def send_list(request):
    send_list = list(models.JobData.objects.filter(sendlist__user=request.session.get("user_id")).values())
    for send in send_list:
        send['send_key'] = 1
    if len(send_list) == 0:
        return JsonResponse({"code": 1, "msg": "没找到需要查询的数据！", "count": "{}".format(len(send_list)), "data": []})
    else:
        return JsonResponse({"code": 0, "msg": "success", "count": "{}".format(len(send_list)), "data": send_list})


def pass_page(request):
    user_obj = models.UserList.objects.filter(user_id=request.session.get("user_id")).first()
    return render(request, "pass_page.html", locals())


def up_info(request):
    if request.method == "POST":
        user_name = request.POST.get("user_name")
        old_pass = request.POST.get("old_pass")
        pass_word = request.POST.get("pass_word")
        user_obj = models.UserList.objects.filter(user_id=request.session.get("user_id")).first()
        if old_pass != user_obj.pass_word:
            return JsonResponse({"Code": 0, "msg": "原密码错误"})
        else:
            models.UserList.objects.filter(user_id=request.session.get("user_id")).update(user_name=user_name,
                                                                                          pass_word=pass_word)
            return JsonResponse({"Code": 0, "msg": "密码修改成功"})


def salary(request):
    return render(request, "salary.html")


def edu(request):
    return render(request, "edu.html")


def bar_page(request):
    return render(request, "bar_page.html")


def bar(request):
    key_list = [x['key_word'] for x in list(models.JobData.objects.all().values("key_word"))]
    # print(key_list)
    bar_x = list(set(key_list))
    # print(bar_x)
    bar_y = []
    for x in bar_x:
        bar_y.append(key_list.count(x))
    # print(bar_y)
    return JsonResponse({"Code": 0, "bar_x": bar_x, "bar_y":bar_y})
