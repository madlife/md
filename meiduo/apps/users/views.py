from django_redis import get_redis_connection
from rest_framework import status
from rest_framework.decorators import action
from rest_framework.generics import CreateAPIView, UpdateAPIView, RetrieveAPIView, ListCreateAPIView
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.viewsets import ModelViewSet

from users import serializers
from users.models import User


class VerifyEmailView(APIView):
    """
    邮箱验证
    """
    def get(self, request):
        # 获取token
        token = request.query_params.get('token')
        if not token:
            return Response({'message': '缺少token'}, status=status.HTTP_400_BAD_REQUEST)

        # 验证token
        user = User.check_verify_email_token(token)
        if user is None:
            return Response({'message': '链接信息无效'}, status=status.HTTP_400_BAD_REQUEST)
        else:
            user.email_active = True
            user.save()
            return Response({'message': 'OK'})


class EmailView(UpdateAPIView):
    """
    保存用户邮箱
    """
    permission_classes = [IsAuthenticated]
    serializer_class = serializers.EmailSerializer

    def get_object(self, *args, **kwargs):
        return self.request.user


class UserView(CreateAPIView):
    """
    用户注册
    传入参数：
        username, password, password2, sms_code, mobile, allow
    """
    serializer_class = serializers.CreateUserSerializer


class UsernameCountView(APIView):
    """ 用户名数量 """
    def get(self, request, username):
        count = User.objects.filter(username=username).count()
        data = {'username': username, 'count': count}
        return Response(data)


class MobileCountView(APIView):
    """ 手机号数量 """

    def get(self, request, mobile):
        count = User.objects.filter(mobile=mobile).count()
        data = {'mobile': mobile, 'count': count}
        return Response(data)


class UserDetailView(RetrieveAPIView):
    # queryset =
    serializer_class = serializers.UserDetailSerializer
    # 必须登录
    permission_classes = [IsAuthenticated]

    # 默认获取一个对象的方法为：根据主键查询
    # 当前逻辑为：哪个用户登录，则显示这个用户的信息
    def get_object(self):
        return self.request.user


class AddressViewSet(ModelViewSet):
    # permission_classes = [IsAuthenticated]

    # retrieve====>无用
    # create===>直接使用
    # update===>直接使用

    # list
    def list(self, request, *args, **kwargs):
        addresses = self.get_queryset()
        serializer = self.get_serializer(addresses, many=True)

        return Response({
            'user_id': request.user.id,
            'default_address_id': request.user.default_address_id,
            'limit': 5,
            'addresses': serializer.data  # [{},{},...]
        })

    # destroy：默认实现是物理删除，当前期望实现逻辑删除
    def destroy(self, request, *args, **kwargs):
        address = self.get_object()
        address.is_delete = True
        address.save()
        return Response(status=204)

    # queryset = Address.objects.all()
    def get_queryset(self):
        # 当前登录用户的未删除的收货地址
        print(f"user: {self.request.user}")
        return self.request.user.addresses.filter(is_deleted=False)

    serializer_class = serializers.AddressSerializer

    # 修改标题===>***/pk/title/  ****/title/
    @action(methods=['put'], detail=True)
    def title(self, request, pk):
        # 接收请求报文中的标题
        title = request.data.get('title')
        # 修改对象的属性
        address = self.get_object()
        address.title = title
        address.save()
        # 响应
        return Response({'title': title})

    # 设置成默认===>****/pk/status/
    @action(methods=['put'], detail=True)
    def status(self, request, pk):
        # 获取当前登录的用户
        user = self.request.user
        # 修改这个用户的默认收货地址
        user.default_address_id = pk
        user.save()
        # 响应
        return Response({'message': 'OK'})
