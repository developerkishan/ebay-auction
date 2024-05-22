from django.contrib.auth.models import AbstractUser
from django.db import models
from django.utils import timezone


class User(AbstractUser):
    pass

class Category(models.Model):
    name = models.CharField(max_length=64, unique=True)

    def __str__(self):
        return self.name


class Listing(models.Model):
    title = models.CharField(max_length=64)
    description = models.TextField(max_length=2000)
    starting_bid = models.DecimalField(max_digits=10,decimal_places=3)
    current_price = models.DecimalField(max_digits=10,decimal_places=3)
    image_url = models.URLField(blank=True , null=True)
    creator = models.ForeignKey(User, on_delete=models.CASCADE)
    created_at = models.DateTimeField(default=timezone.now)
    is_active = models.BooleanField(default=True)
    category = models.ForeignKey(Category,on_delete=models.CASCADE,related_name="listing")

    def __str__(self):
        return self.title


class Bid(models.Model):
    listing = models.ForeignKey(Listing,on_delete=models.CASCADE)
    bidder = models.ForeignKey(User,on_delete=models.CASCADE)
    bid_amount = models.DecimalField(max_digits=10,decimal_places=2)
    bid_time = models.DateTimeField(default=timezone.now)
    
    def __str__(self):
        return f"{self.bidder.username} bid {self.bid_amount} on {self.listing.title}"
    



class Comment(models.Model):
    listing = models.ForeignKey(Listing,on_delete=models.CASCADE)
    commenter = models.ForeignKey(User,on_delete=models.CASCADE)
    comment_text = models.TextField(max_length=2000)
    comment_time = models.DateTimeField(default=timezone.now)

    def __str__(self):
        return f"{self.commenter.username} commented on {self.listing.title} at {self.comment_time}"


class Watchlist(models.Model):
    listing = models.ForeignKey(Listing,on_delete=models.CASCADE)
    user = models.ForeignKey(User,on_delete=models.CASCADE)

    def __str__(self):
        return f"{self.user.username} is watching {self.listing.title}"
    
