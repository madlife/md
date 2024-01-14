from rest_framework.routers import DefaultRouter
from . import views


urlpatterns = [

]

router = DefaultRouter()
# 自动生成单数、复数的路由规则
router.register('areas', views.AreaViewSet, basename='areas')
urlpatterns += router.urls
