from rest_framework import viewsets
from rest_framework.views import APIView
import pyotp
from rest_framework.response import Response
from rest_framework.exceptions import AuthenticationFailed
from .serializers import UserSerializer, ProfileSerializer, FriendSerializer, GameHistorySerializer
from .models import User , Profile, Friend, GameHistory
import jwt, datetime

class RegisterView(APIView):
    def post(self, request):
        serializer = UserSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(serializer.data)

class LoginView(APIView):
    def post(self, request):
        email = request.data['email']
        password = request.data['password']

        user = User.objects.filter(email=email).first()

        if user is None:
            raise AuthenticationFailed('User not found!')

        if not user.check_password(password):
            raise AuthenticationFailed('Incorrect password!')

        payload = {
            'id': user.id,
            'exp': datetime.datetime.utcnow() + datetime.timedelta(minutes=60),
            'iat': datetime.datetime.utcnow()
        }

        token = jwt.encode(payload, 'secret', algorithm='HS256')


        response = Response()

        response.set_cookie(key='jwt', value=token, httponly=True)
        response.data = {
            'jwt': token
        }
        return response

class UserListView(APIView):
    def get(self, request):
        users = User.objects.all()
        serializer = UserSerializer(users, many=True)
        return Response(serializer.data)

class UserView(APIView):
    def get(self, request):
        token = request.COOKIES.get('jwt')
        if not token:
            raise AuthenticationFailed ('Unauthenticated!@@@@@')
        try:
            payload=jwt.decode(token, 'secret', algorithms=['HS256'])
        except jwt.ExpiredSignatureError:
            raise AuthenticationFailed ('Unauthenticated!')

        user = User.objects.filter(id=payload['id']).first()
        serializer = UserSerializer(user)
        return Response (serializer.data)

class LogoutView(APIView):
    def post(self, request):
        response = Response()
        response.delete_cookie('jwt')
        response.data = {
            'message': 'success'
        }
        return response

class ProfileViewSet(viewsets.ModelViewSet):
    queryset = Profile.objects.all()
    serializer_class = ProfileSerializer

class TwoFactorAuthView(APIView):
    def get(self, request):
        user = request.user
        secret = pyotp.random_base32()
        user.profile.otp_secret = secret
        user.profile.save()
        otp_uri = pyotp.totp.TOTP(secret).provisioning_uri(name=user.email, issuer_name="Big Bong Game")
        qr_code = pyotp.utils.make_qrcode(otp_uri)
        return Response({'qr_code': qr_code})

    def post(self, request):
        user = request.user
        otp_secret = user.profile.otp_secret
        otp_code = request.data.get('otp_code')
        totp = pyotp.TOTP(otp_secret)
        if totp.verify(otp_code):
            user.profile.is_2fa_enabled = True
            user.profile.save()
            return Response({'status': '2FA enabled'})
        return Response({'error': 'Invalid code'}, status=400)

class FriendViewSet(viewsets.ModelViewSet):
    queryset = Friend.objects.all()
    serializer_class = FriendSerializer

class GameHistoryViewSet(viewsets.ModelViewSet):
    queryset = GameHistory.objects.all()
    serializer_class = GameHistorySerializer
