from django.urls import path

from .views import PartyViewSet

urlpatterns = [
    path('', PartyViewSet.as_view({'get': 'list',
                                   'post': 'create'})),
    path('mine/', PartyViewSet.as_view({'get': 'list_mine'})),
    path('<uuid:public_id>/', PartyViewSet.as_view({'get': 'retrieve',
                                                    'put': 'update',
                                                    'patch': 'partial_update',
                                                    'delete': 'destroy'})),
]
