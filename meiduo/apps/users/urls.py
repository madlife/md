from rest_framework.routers import DefaultRouter

from apps.users import views
from django.conf.urls import url
from rest_framework_jwt.views import obtain_jwt_token

urlpatterns = [
    url(r'^authorizations/$', obtain_jwt_token),
    url(r'^usernames/(?P<username>\w{5,20})/count/$', views.UsernameCountView.as_view()),
    url(r'^mobiles/(?P<mobile>1[3-9]\d{9})/count/$', views.MobileCountView.as_view()),
    url(r'^users/$', views.UserView.as_view()),
    url('^user/$', views.UserDetailView.as_view()),
    url(r'^emails/$', views.EmailView.as_view()),  # 设置邮箱
    url(r'^emails/verification/$', views.VerifyEmailView.as_view()),
]

router = DefaultRouter()
router.register('addresses', views.AddressViewSet, basename='addresses')
urlpatterns += router.urls
