from django.urls import path

from . import views

urlpatterns = [
    path('', views.IndexView.as_view(),name='index'),
    path('suggest/',views.SuggestView.as_view(),name='suggest'),
    path('heading/',views.HeadingView.as_view(),name='heading'),
    path('chrcount/',views.ChrCountView.as_view(),name='chrcount'),
    path('realtimecnt/',views.RealTimeCntView.as_view(),name='realtimecnt'),
    path('whois/',views.WhoIsView.as_view(),name='whois'),
    path('replace/',views.ReplaceView.as_view(),name='replace'),
    path('frequent/',views.FrequentWordView.as_view(),name='frequent'),
    path('animbutton/',views.AnimButton.as_view(),name='animbutton'),
    path('linkopener/',views.LinkOpenerView.as_view(),name='linkopener'),
    path('allintitle/',views.AllInTitleView.as_view(),name='allintitle'),
]