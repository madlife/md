from django.conf.urls import url
from . import views

urlpatterns = [
    url('^qq/authorization/$', views.QQurlView.as_view()),
    url('^qq/user/$', views.QQLoginBindView.as_view()),
]
