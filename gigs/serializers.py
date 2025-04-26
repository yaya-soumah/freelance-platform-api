from rest_framework import serializers
from .models import Gig, Bid, Review, Profile

class ProfileSerializer(serializers.ModelSerializer):
    class Meta:
        model = Profile
        fields = ['role','wallet','reputation']

class BidSerializer(serializers.ModelSerializer):
    freelancer = serializers.StringRelatedField()
    class Meta:
        model = Bid
        fields = ['id','gig', 'freelancer', 'amount', 'message', 'created_at', 'accepted']

class GigSerializer(serializers.ModelSerializer):
    bids = BidSerializer(many=True, read_only=True)
    client = serializers.StringRelatedField()
    accepted_bid = BidSerializer( read_only=True)
    class Meta:
        model = Gig
        fields = ['id', 'client','title', 'description', 'budget',
                  'deadline', 'status','created_at','bids','accepted_bid','payment_deposited','payment_released']

class ReviewSerializer(serializers.ModelSerializer):
    freelancer = serializers.StringRelatedField()
    class Meta:
        model = Review
        fields = ['id', 'gig', 'freelancer', 'rating', 'comment','created_at']