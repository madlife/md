from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

from . import serializers
from .qq_sdk import OAuthQQ
from .models import QQUser
from utils.jwt_token import generate_jwt_token
from itsdangerous import TimedJSONWebSignatureSerializer as TJWSSerializer
from django.conf import settings
from rest_framework.generics import CreateAPIView, RetrieveAPIView
from .serializers import QQBindSerializer
# from carts.utils import merge_cookie_to_redis


# 返回QQ的授权url
class QQurlView(APIView):
    def get(self, request):
        state = request.query_params.get('next')
        # 构造url地址及参数
        oauthQQ = OAuthQQ(state=state)
        login_url = oauthQQ.get_qq_login_url()

        # 返回地址
        return Response({
            'login_url': login_url
        })


class QQLoginBindView(APIView):
    # 授权登录
    def get(self, request):
        # 接收code，获取token，再获取openid
        # 1.接收code
        code = request.query_params.get('code')
        # 2.获取token
        oauthqq = OAuthQQ()
        token = oauthqq.get_access_token(code)
        # 3.获取openid
        openid = oauthqq.get_openid(token)

        # 判断openid是否存在
        try:
            qquser = QQUser.objects.get(openid=openid)
        except QQUser.DoesNotExist:
            # 如果不存在，则返回绑定页面
            # 创建加密对象
            serializer = TJWSSerializer(settings.SECRET_KEY, 60 * 10)
            # 将openid进行加密，转成字符串
            token = serializer.dumps({'openid': openid}).decode()
            # 将包含openid的加密字符串，返回给客户端
            return Response({
                'access_token': token
            })
        else:
            response = Response({
                'user_id': qquser.user.id,
                'username': qquser.user.username,
                'token': generate_jwt_token(qquser.user)
            })
            # 授权登录成功，合并购物车信息
            # response = merge_cookie_to_redis(request, qquser.user.id, response)
            # 如果存在则获取对应的user对象，构造jwt——token并返回
            return response

    # 绑定账号
    def post(self, request):
        # 接收
        serializer = QQBindSerializer(data=request.data)
        # 验证
        if not serializer.is_valid():
            return Response({'message': serializer.errors})
        # 保存
        qquser = serializer.save()
        # 响应
        response = Response({
            'user_id': qquser.user.id,
            'username': qquser.user.username,
            'token': generate_jwt_token(qquser.user)
        })
        # 授权登录成功，合并购物车信息
        # response = merge_cookie_to_redis(request, qquser.user.id, response)
        # 如果存在则获取对应的user对象，构造jwt——token并返回
        return response

# #让qq账号与现有账号绑定：数据操作为向qq表中添加数据
# class QQBindView(CreateAPIView):
#     serializer_class = QQBindSerializer


class UserDetailView(RetrieveAPIView):
    """
    用户详情: 访问视图必须要求用户已通过认证（即登录之后）
    """
    serializer_class = serializers.UserDetailSerializer
    permission_classes = [IsAuthenticated]

    def get_object(self):
        return self.request.user
