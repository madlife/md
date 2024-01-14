from itsdangerous import TimedJSONWebSignatureSerializer as TJWSSerializer
from django.conf import settings


def generate_save_user_token(openid):
    """
    生成保存用户数据的token
    :param openid: 用户的openid
    :return: token
    """
    serializer = TJWSSerializer(settings.SECRET_KEY, expires_in=600)
    data = {'openid': openid}
    token = serializer.dumps(data)
    return token.decode()
