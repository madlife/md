from django.urls import path
from apps.verifications import views
from django.conf.urls import url, include

urlpatterns = [
    url(r'^sms_code/(?P<mobile>1[3-9]\d{9})/$', views.SMSCodeView.as_view()),
]
