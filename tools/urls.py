from django.urls import path

from . import views

urlpatterns = [
    path('', views.IndexView.as_view(),name='index'),
    path('suggest/',views.SuggestView.as_view(),name='suggest'),
    path('heading/',views.HeadingView.as_view(),name='heading'),
    path('chrcount/',views.ChrCountView.as_view(),name='chrcount'),
    path('realtimecnt/',views.RealTimeCnt.as_view(),name='realtimecnt'),
]