from celery import shared_task
from .models import Review, Profile
from django.db.models import F

@shared_task
def update_reputation(freelancer_id, reputation):
    reviews = Review.objects.filter(freelancer_id=freelancer_id).order_by('-created_at')[:5]
    if not reviews:
        return
    total = sum(r.rating * (0.9 ** i) for i, r in enumerate(reviews))
    weight = sum(0.9 ** i for i in range(len(reviews)))
    reputation = total / weight if weight else 0
    Profile.objects.filter(user_id=freelancer_id).update(reputation=reputation)