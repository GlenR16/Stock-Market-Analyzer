from django.urls import path
from .views import IndexView,LogoutView,LoginView,PasswordChangeView,DashboardView,AboutUsView,FaviconView,RssView

urlpatterns = [
    path("",IndexView.as_view(),name="index"), # Landing page that user will see.
    path("login/",LoginView.as_view(),name="login"), # User can login here.
    path("logout/",LogoutView.as_view(),name="logout"), # User can login here.
    path("change_password/",PasswordChangeView.as_view(),name="change_password"), # User can change their password here.
    path("dashboard/",DashboardView.as_view(),name="dashboard"), # Main Dashboard here.
    path("aboutus/",AboutUsView.as_view(),name="about"), # Feedback Page
    path('favicon.ico', FaviconView), # For favicon
    path('rss/',RssView.as_view(),name='rss'),
    # path('api/',views.api,name='api'),
]