from django.urls import path
from .views import RegisterView, LoginView, UserView, LogoutView, UserListView
from rest_framework.routers import DefaultRouter
from django.urls import path, include
from .views import ProfileViewSet, TwoFactorAuthView, FriendViewSet, GameHistoryViewSet

router = DefaultRouter()
router.register(r'profiles', ProfileViewSet)
router.register(r'friends', FriendViewSet)
router.register(r'game-history', GameHistoryViewSet)

urlpatterns = [
    path('register', RegisterView.as_view()),
    path('login', LoginView.as_view()),
    path('user', UserView.as_view()),
    path('logout', LogoutView.as_view()),
    path('listing', UserListView.as_view()),
    path('router', include(router.urls)),
    path('2fa/', TwoFactorAuthView.as_view(), name='2fa'),
]
