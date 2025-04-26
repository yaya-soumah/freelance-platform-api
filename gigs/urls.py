from django.urls import path, include
from rest_framework.routers import DefaultRouter
from views import GigViewSet, BidViewSet, ReviewViewSet

router = DefaultRouter()
router.register('gigs', GigViewSet, basename='gigs')
router.register('bids', BidViewSet, basename='bids')
router.register('reviews', ReviewViewSet, basename='reviews')

urlpatterns = [
    path('', include(router.urls)),
]