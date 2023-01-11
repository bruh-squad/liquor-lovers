from django.urls import path

from .views import InvitationViewSet, FriendViewSet

urlpatterns = [
    path('', FriendViewSet.as_view({'get': 'list'})),
    path('<uuid:public_id>/', FriendViewSet.as_view({'delete': 'destroy'})),

    path('invitations/', InvitationViewSet.as_view({'post': 'create',
                                                    'get': 'list',
                                                    'delete': 'destroy'})),
    path('invitations/my/', InvitationViewSet.as_view({'get': 'list_from_me'})),
    path('invitations/<int:pk>/', InvitationViewSet.as_view({'post': 'accept',
                                                             'delete': 'destroy'}))
]
