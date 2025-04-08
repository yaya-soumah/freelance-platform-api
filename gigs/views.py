from asgiref.sync import async_to_sync
from channels.layers import get_channel_layer
from django.db import transaction
from rest_framework import viewsets, permissions, serializers, status
from rest_framework.decorators import action
from rest_framework.response import Response
from gigs.models import Gig, Bid, Review
from gigs.serializers import GigSerializer, BidSerializer, ReviewSerializer
from gigs.tasks import update_reputation


class GigViewSet(viewsets.ModelViewSet):
    queryset = Gig.objects.all()
    serializer_class = GigSerializer
    permission_classes = [permissions.IsAuthenticated, ]

    def perform_create(self, serializer):
        serializer.save(client=self.request.user)

    def get_queryset(self):
        if self.request.user.profile.role == 'client':
            return Gig.objects.filter(client=self.request.user)
        return Gig.objects.filter(status='open')

    @action(detail=True, methods=['post'])
    def accept_bid(self, request, pk=None):
        gig = self.get_object()
        if gig.client != request.user or gig.status != 'open':
            return Response({'detail': 'Cannot accept bid on this gig'}, status=status.HTTP_400_BAD_REQUEST)
        bid_id = request.data.get('bid_id')
        try:
            with transaction.atomic():
                bid = Bid.objects.get(id=bid_id, gig=gig)
                if bid.accepted:
                    return Response({'detail': 'Bid already accepted'}, status=status.HTTP_400_BAD_REQUEST)
                bid.accepted_bid = bid
                bid.accepted = True
                bid.save()
                gig.status = 'in_progress'
                gig.save()
                return Response({'detail': 'Bid accepted', 'bid_id': bid.id}, status=status.HTTP_200_OK)
        except Bid.DoesNotExist:
            return Response({'detail': 'Bid not found'}, status=status.HTTP_404_NOT_FOUND)

    @action(detail=True, methods=['post'])
    def deposit_payment(self,request, pk=None):
        gig = self.get_object()
        if gig.client != request.user or gig.status != 'in_progress' or gig.payment_deposited:
            return Response({'detail':'Cannot deposit payment on this gig'}, status=status.HTTP_400_BAD_REQUEST)
        profile = request.user.profile
        if profile.wallet < gig.budget:
            return Response({'detail':'Insufficient funds!'}, status=status.HTTP_400_BAD_REQUEST)
        with transaction.atomic():
            profile.wallet -= gig.budget
            profile.save()
            gig.payment_deposited = True
            gig.save()
            #Send Websocket notification
            channel_layer = get_channel_layer()
            async_to_sync(channel_layer.group_send)(
                f'gig_{gig.id}',
                {
                    'type': 'payment_deposited',
                    'payment': {
                        'gig_id': gig.id,
                        'amount': str(gig.budget),
                        'timestamp': gig.created_at.isoformat(),
                    }
                }

            )
        return Response({'detail':'Payment deposited'})

    @action(detail=True, methods=['post'])
    def complete_gig(self, request, pk=None):
        gig = self.get_object()
        if gig.client != request.user or gig.status != 'in_progress' or not gig.payment_deposited:
            return Response({'detail': 'Cannot complete gig'}, status=status.HTTP_400_BAD_REQUEST)
        with transaction.atomic():
            gig.status = 'completed'
            gig.payment_released = True
            freelancer_profile = gig.accepted_bid.freelancer.profile
            freelancer_profile.wallet += gig.accepted_bid.amount
            freelancer_profile.save()
            gig.save()
            #Send Websocket notification
            channel_layer = get_channel_layer()
            async_to_sync(channel_layer.group_send)(
                f'gig_{gig.id}',
                {
                    'type': 'gig_completed',
                    'completion': {
                        'gig_id': gig.id,
                        'freelancer': gig.accepted_bid.freelancer.username,
                        'amount': str(gig.accepted_bid.amount),
                        'timestamp': gig.created_at.isoformat(),
                    }
                }
            )
        return Response({'detail': 'Gig completed, payment released'})



class BidViewSet(viewsets.ModelViewSet):
    queryset = Bid.objects.all()
    serializer_class = BidSerializer
    permission_classes = [permissions.IsAuthenticated, ]

    def perform_create(self, serializer):
        if self.request.user.profile.role != 'freelancer':
            raise serializers.ValidationError('Only freelancer can Bid')
        serializer.save(freelancer=self.request.user)
        # Send Websocket notification
        gig =  serializer.validated_data['gig']
        channel_layer = get_channel_layer()
        async_to_sync(channel_layer.group_send)(
            f'gig_{gig.id}',
            {
                'type': 'bid_update',
                'bid': {
                    'id': serializer.instance.id,
                    'freelancer': self.request.user.username,
                    'amount': str(serializer.instance.amount),
                    'message': serializer.instance.message,
                    'created_at': serializer.instance.created_at.isoformat(),
                }
            }
        )

class ReviewViewSet(viewsets.ModelViewSet):
    queyset = Review.objects.all()
    serializer_class = ReviewSerializer
    permission_classes = [permissions.IsAuthenticated, ]

    def perform_create(self, serializer):
        gig = serializer.validated_data['gig']
        if gig.client != self.request.user or gig.status != 'completed':
            raise serializers.ValidationError('Cannot review review on this gig')
        review = serializer.save(freelancer=gig.accepted_bid.freelancer )
        update_reputation.delay(review.freelancer.id)



