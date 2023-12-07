from django.urls import path

from .views import *


urlpatterns = [
    path('signup/', SignUpView.as_view(), name='signup'),
    path('activate/<uidb64>/<token>/', activate, name='activate'),
    path('login/', LoginView.as_view(), name='login'),
    path('logout/', logout_view, name='logout'),
    path('my-profile/', MyProfileView.as_view(), name='my_profile'),
    path('my-profile/<int:pk>/delete/', DeleteUserView.as_view(), name='delete_user'),
    path('check-username-exists/', check_username_exists, name='check_username_exists'),
    path('premium/', PremiumView.as_view(), name='premium'),
    path('get-premium/', GetPremiumView.as_view(), name='get_premium'),
    path('cancel-premium/', CancelPremiumView.as_view(), name='cancel_premium'),
]
