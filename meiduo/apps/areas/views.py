from rest_framework import viewsets
from rest_framework_extensions.cache.mixins import CacheResponseMixin
from areas import serializers
from areas.models import Area


class AreaViewSet(CacheResponseMixin, viewsets.ReadOnlyModelViewSet):
    # list
    # retrieve
    # serializer_class = serializers.AreaSubsSerializer
    def get_serializer_class(self):
        if self.action == 'list':
            # 查询多个，当前为省列表，输出id、name
            return serializers.AreaSerializer
        else:
            # 查询一个，输出id、name、子级地区，格式为id、name
            return serializers.AreaSubsSerializer

    # queryset = Area.objects.all()
    def get_queryset(self):
        if self.action == 'list':
            # 查询多个时，返回所有的省
            return Area.objects.filter(parent__isnull=True)
        else:
            # 查询1个时，根据pk在如下范围内查询
            return Area.objects.all()
