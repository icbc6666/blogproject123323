from django.conf.urls import url
from django.contrib import admin
from django.urls import path
from . import views
from django.conf import settings
from django.conf.urls.static import static
from django.utils.decorators import method_decorator

app_name='blog'
urlpatterns = [
   # 文章的首页
   url(r"^$",  views.IndexView.as_view(), name='index'),
   # 详情页
   url(r"^post/(?P<pk>[0-9]+)/$", views.detail, name="detail"),
   # 归档页
   url(r"^archives/(?P<year>[0-9]{4})/(?P<month>[0-9]{1,2})/$", views.ArchivesView.as_view(), name="archives"),
   # 分类
   url(r"^category/(?P<pk>[0-9]+)/$", views.CategoryView.as_view(), name="category"),
   url(r"^tag/(?P<pk>[0-9]+)/$",views.TagView.as_view(), name='tag'),
   url(r"^full_width/$",views.full_width, name='full_width'),
   url(r"^about/$",views.about, name='about'),
   url(r"^contact/$",views.contact, name='contact'),
]