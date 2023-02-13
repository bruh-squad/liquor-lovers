from django.urls import path

from .views import PartyViewSet, PartyInvitationViewSet

urlpatterns = [
    path('', PartyViewSet.as_view({'get': 'list',
                                   'post': 'create'})),
    path('mine/', PartyViewSet.as_view({'get': 'list_mine'})),
    path('<uuid:public_id>/', PartyViewSet.as_view({'get': 'retrieve',
                                                    'put': 'update',
                                                    'patch': 'partial_update',
                                                    'delete': 'destroy'})),

    path('invitations/', PartyInvitationViewSet.as_view({'get': 'list_mine'})),
    path('invitations/<uuid:party_public_id>/', PartyInvitationViewSet.as_view({'get': 'list',
                                                                                'post': 'create'})),
    path('invitations/<uuid:party_public_id>/<int:pk>/',
         PartyInvitationViewSet.as_view({'get': 'list', 'post': 'accept', 'delete': 'destroy'}))
]
