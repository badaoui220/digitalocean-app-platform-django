from django.contrib import admin
from django.urls import path, re_path
from django.conf.urls import include, url
from rest_framework import routers
from .views import UserViewSet, PaieViewSet, ConsultantViewSet, CustomObtainAuthToken, ConsultantListBytype, LogView

router = routers.DefaultRouter()
router.register('paies', PaieViewSet)
router.register('consultants', ConsultantViewSet)

urlpatterns = [
    path('', include(router.urls)),
    url(r'^login/', CustomObtainAuthToken.as_view()),
    url(r'^log/', LogView.as_view()),
    re_path('^guests/(?P<structure>.+)/$', ConsultantListBytype.as_view()),
]
