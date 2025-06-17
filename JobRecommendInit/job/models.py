# This is an auto-generated Django model module.
# You'll have to do the following manually to clean this up:
#   * Rearrange models' order
#   * Make sure each model has one field with primary_key=True
#   * Make sure each ForeignKey and OneToOneField has `on_delete` set to the desired behavior
#   * Remove `managed = True` lines if you wish to allow Django to create, modify, and delete the table
# Feel free to rename the models, but don't rename db_table values or field names.
from django.db import models





from django.db import models

class JobData(models.Model):
    job_id = models.AutoField('职位ID', primary_key=True)  # 职位ID，自动增长主键
    name = models.CharField('职位名称', max_length=255, blank=True, null=True)  # 职位名称
    salary = models.CharField('薪资', max_length=255, blank=True, null=True)  # 薪资
    place = models.CharField('工作地点', max_length=255, blank=True, null=True)  # 工作地点
    education = models.CharField('学历要求', max_length=255, blank=True, null=True)  # 学历要求
    experience = models.CharField('工作经验', max_length=255, blank=True, null=True)  # 工作经验
    company = models.CharField('公司名称', max_length=255, blank=True, null=True)  # 公司名称
    label = models.CharField('职位标签', max_length=255, blank=True, null=True)  # 职位标签
    scale = models.CharField('公司规模', max_length=255, blank=True, null=True)  # 公司规模
    href = models.CharField('职位链接', max_length=255, blank=True, null=True)  # 职位链接
    key_word = models.CharField('关键词', max_length=255, blank=True, null=True)  # 关键词

    class Meta:
        managed = True  # 是否由Django管理
        db_table = 'job_data'  # 数据库表名
        verbose_name = "招聘信息"
        verbose_name_plural = "招聘信息"


class SendList(models.Model):
    send_id = models.AutoField(primary_key=True)
    job = models.ForeignKey(JobData, models.DO_NOTHING, blank=True, null=True)
    user = models.ForeignKey('UserList', models.DO_NOTHING, blank=True, null=True)

    class Meta:
        managed = True
        db_table = 'send_list'


class SpiderInfo(models.Model):
    spider_id = models.AutoField(primary_key=True)
    spider_name = models.CharField(max_length=255, blank=True, null=True)
    count = models.IntegerField(blank=True, null=True)
    page = models.IntegerField(blank=True, null=True)

    class Meta:
        managed = True
        db_table = 'spider_info'


class UserExpect(models.Model):
    expect_id = models.AutoField(primary_key=True)
    key_word = models.CharField(max_length=255, blank=True, null=True)
    user = models.ForeignKey('UserList', models.DO_NOTHING, blank=True, null=True)
    place = models.CharField(max_length=255, blank=True, null=True)

    class Meta:
        managed = True
        db_table = 'user_expect'



class UserList(models.Model):
    user_id = models.CharField('用户ID', primary_key=True, max_length=11)  # 用户ID，主键
    user_name = models.CharField('用户名', max_length=255, blank=True, null=True)  # 用户名
    pass_word = models.CharField('密码', max_length=255, blank=True, null=True)  # 密码

    class Meta:
        managed = True  # 是否由Django管理
        db_table = 'user_list'  # 数据库表名
        verbose_name = "前台用户"
        verbose_name_plural = "前台用户"