import json
from channels.generic.websocket import AsyncWebsocketConsumer
from channels.db import database_sync_to_async
from django.core.exceptions import ValidationError

from .models import Bid, Gig

class BidConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        self.gig_id = self.scope['url_route']['kwargs']['gig_id']
        self.group_name = f'gig_{self.gig_id}'

        # check if gig exists and is open
        if await self.gig_exists():
            await self.channel_layer.group_add(self.group_name, self.channel_name)
            await self.accept()
        else:
            await self.close(code=4003)

    async def disconnect(self, close_code):
        await self.channel_layer.group_discard(self.group_name, self.channel_name)

    async def receive(self, text_data):
        try:
            data = json.loads(text_data)
        except json.JSONDecodeError:
            await self.send(text_data=json.dumps({'error': 'invalid json'}))
            return
        if self.scope['user'].is_anonymous or self.scope['user'].profile.role != 'freelancer':
            await self.send(text_data=json.dumps({'error': 'Only freelancers can bid'}))
            return

        try:
            bid = await self.create_bid(
                gig_id=data.get('gig_id'),
                amount=data.get('amount'),
                message=data.get('message'),
            )
            if bid:
                await self.notify_group(bid)
        except ValidationError as e:
            await self.send(text_data=json.dumps({'error': str(e)}))

    async def notify_group(self, bid):
        await self.channel_layer.group_send(self.group_name, {
            'type': 'bid_update',
            'bid': {
                'id': bid.id,
                'freelancer': bid.freelancer.username,
                'amount': str(bid.amount),
                'message': bid.message,
                'created_at': bid.created_at.isoformat(),
            }
        })

    async def bid_update(self, event):
        await self.send(text_data=json.dumps({'type':'bid','data':event['bid']}))

    async def payment_deposited(self,event):
        await self.send(text_data=json.dumps({'type':'payment_deposited','data':event['payment']}))

    async def gig_completed(self,event):
        await self.send(text_data=json.dumps({'type':'gig_completed','data':event['completion']}))


    @database_sync_to_async
    def gig_exists(self):
        return Gig.objects.filter(gig_id=self.gig_id).exists()

    @database_sync_to_async
    def create_bid(self, gig_id, amount, message):
        try:
            gig = Gig.objects.get(id=gig_id, status='open')

            # Prevent freelancers from bidding on their own gigs
            if gig.client == self.scope['user']:
                raise ValidationError('You cannot bid on your own gig')

            if float(amount) <= 0:
                raise ValidationError('Bid amount must be a positive number')

            return Bid.objects.create(
                gig=gig,
                freelancer=self.scope['user'],
                amount=amount,
                message=message,
            )
        except Gig.DoesNotExist:
            raise ValidationError('Gig not found or not open for bidding')
        except ValueError:
            raise ValidationError('Bid amount is invalid')