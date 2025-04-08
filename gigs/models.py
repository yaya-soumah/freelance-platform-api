from django.db import models
from django.contrib.auth.models import User

class Profile(models.Model):
    USER_ROLES = (('client', 'Client'), ('freelancer', 'Freelancer'))
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    role = models.CharField(max_length=10, choices=USER_ROLES)
    wallet = models.DecimalField(max_digits=10, decimal_places=2, default=0.00)
    reputation = models.FloatField(default=0.0)

    def __str__(self):
        return f"{self.user.username} ({self.role})"

class Gig(models.Model):
    STATUS_CHOICES = (('open', 'Open'), ('in_progress', 'In Progress'), ('completed', 'Completed'))
    client = models.ForeignKey(User, on_delete=models.CASCADE, related_name='gigs')
    title = models.CharField(max_length=100)
    description = models.TextField()
    budget = models.DecimalField(max_digits=10, decimal_places=2)
    deadline = models.DateTimeField()
    status = models.CharField(max_length=12, choices=STATUS_CHOICES, default='open')
    created_at = models.DateTimeField(auto_now_add=True)
    accepted_bid = models.OneToOneField('Bid', on_delete=models.SET_NULL, null=True, blank=True, related_name='accepted_bid')
    payment_deposited = models.BooleanField(default=False)
    payment_released = models.BooleanField(default=False)

    def __str__(self):
        return self.title

class Bid(models.Model):
    gig = models.ForeignKey(Gig, on_delete=models.CASCADE, related_name='bids')
    freelancer = models.ForeignKey(User, on_delete=models.CASCADE)
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    message = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)
    accepted = models.BooleanField(default=False)

    def __str__(self):
        return f"{self.freelancer.username} bid {self.amount} on {self.gig.title}"

class Review(models.Model):
    gig = models.OneToOneField(Gig, on_delete=models.CASCADE)
    freelancer = models.ForeignKey(User, on_delete=models.CASCADE)
    rating = models.IntegerField(choices=[(i, i) for i in range(1, 6)])
    comment = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.rating} stars for {self.freelancer.username}"