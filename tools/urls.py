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
    path('yahookeyword/',views.YahooKeywordView.as_view(),name='yahookeyword'),
    path('kousei/',views.KouseiView.as_view(),name='kousei'),
    path('kousei-f/',views.KouseiFView.as_view(),name='kousei-f'),
    path('wordcloud/',views.WordCloudView.as_view(),name='wordcloud'),
    path('htmlmail/',views.HtmlMailView.as_view(),name='htmlmail'),
    path('domain-age/',views.DomainAgeView.as_view(),name='domain-age'),
]