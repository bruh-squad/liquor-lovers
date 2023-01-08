from django.urls import path

from .views import UserViewSet

urlpatterns = [
    path('', UserViewSet.as_view({'post': 'create',
                                  'get': 'retrieve',
                                  'put': 'update',
                                  'patch': 'partial_update',
                                  'delete': 'destroy'})),

    path('<uuid:public_id>/', UserViewSet.as_view({'get': 'retrieve_other'})),
]
