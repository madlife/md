from rest_framework import serializers
from users.models import User
from .models import QQUser
from itsdangerous import TimedJSONWebSignatureSerializer as TJWSSerializer
from django.conf import settings


class UserDetailSerializer(serializers.ModelSerializer):
    """
    用户详细信息序列化器
    """
    class Meta:
        model = User
        fields = ('id', 'username', 'mobile', 'email', 'email_active')


class QQBindSerializer(serializers.Serializer):
    # 定义属性
    mobile = serializers.CharField()
    password = serializers.CharField()
    sms_code = serializers.CharField()
    access_token = serializers.CharField()

    # 编写验证方法
    def validate(self, attrs):
        # 短信验证码：
        # 1.读取请求中的验证码
        # 2.读取redis中的验证码
        # 3.判断redis中的验证码是否过期
        # 4.删除redis中的验证码
        # 5.比较

        # 密码的长度验证
        # 手机号格式验证

        # 验证access_token
        serializer = TJWSSerializer(settings.SECRET_KEY, 600)
        try:
            # 解密，获取openid
            data = serializer.loads(attrs.get('access_token'))
            attrs['openid'] = data.get('openid')
        except:
            raise serializers.ValidationError('access_token无效')

        return attrs

    # 编写创建方法
    def create(self, validated_data):
        mobile = validated_data.get('mobile')
        password = validated_data.get('password')
        # 根据手机号查询User对象
        try:
            user = User.objects.get(mobile=mobile)
        except:
            # 如果没有则创建User对象再绑定
            user = User()
            user.username = mobile
            user.mobile = mobile
            user.set_password(password)
            user.save()
        else:
            # 如果有则判断密码再绑定
            if not user.check_password(password):
                raise serializers.ValidationError('此手机号已经被其它人使用')

        # 创建QQ授权对象
        qquser = QQUser()
        qquser.openid = validated_data.get('openid')
        qquser.user = user
        qquser.save()

        return qquser
