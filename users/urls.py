from django.urls import path
from .views import WalletConnectView, GrantAccessView, CheckAccessView, get_user_points

urlpatterns = [
    path('create/', WalletConnectView.as_view(), name='user-create'),
    path('grant-access/', GrantAccessView.as_view(), name='grant-access'),
    path('check-access/', CheckAccessView.as_view(), name='check-access'),
    path('points/', get_user_points),
]
