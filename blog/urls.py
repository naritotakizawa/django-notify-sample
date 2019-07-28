from django.urls import path
from .feeds import LatestPostFeed
from . import views

app_name = 'blog'

urlpatterns = [
    path('', views.subscribe, name='subscribe'),  # 購読ページ
    path('latest/feed/', LatestPostFeed(), name='feed'),  # フィード配信

    # メール購読関連
    path('subscribe/thanks/', views.subscribe_thanks, name='subscribe_thanks'),
    path('subscribe/register/<str:token>/', views.subscribe_register, name='subscribe_register'),
    path('subscribe/done/', views.subscribe_done, name='subscribe_done'),

    # resolve_url()等で使えるように、便宜的に定義
    path('list/', views.PostIndex.as_view(), name='list'),
    path('detail/<int:pk>/', views.PostDetail.as_view(), name='detail'),

    # Line 友達追加のWeb hook
    path('callback/', views.callback, name='callback')
]
