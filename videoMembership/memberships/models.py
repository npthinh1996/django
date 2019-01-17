from django.db import models
from django.conf import settings
from django.dispatch import receiver
from django.db.models.signals import post_save
import stripe

stripe.api_key = settings.STRIPE_SECRET_KEY

MEMBERSHIP_CHOICES = [
    ('Enterprise', 'ent'),
    ('Professional', 'pro'),
    ('Free', 'free')
]

class Membership(models.Model):
    slug = models.SlugField()
    membership_type = models.CharField(choices=MEMBERSHIP_CHOICES, default='free', max_length=30)
    price = models.IntegerField(default=15)
    stripe_plan_id = models.CharField(max_length=40)

    def __str__(self):
        return self.membership_type

class UserMembership(models.Model):
    user = models.OneToOneField(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    stripe_customer_id = models.CharField(max_length=40)
    membership = models.ForeignKey(Membership, on_delete=models.SET_NULL, null=True)

    def __str__(self):
        return self.user.username

@receiver(post_save, sender=settings.AUTH_USER_MODEL)
def post_save_usermembership_create(instance, **kwargs):
    user_membership = UserMembership.objects.get_or_create(user=instance)[0]
    if user_membership.stripe_customer_id is None or user_membership.stripe_customer_id == '':
        new_customer_id = stripe.Customer.create(email=instance.email)
        user_membership.stripe_customer_id = new_customer_id['id']
        user_membership.save()

class Subscription(models.Model):
    user_membership = models.ForeignKey(UserMembership, on_delete=models.CASCADE)
    stripe_supscription_id = models.CharField(max_length=40)
    active = models.BooleanField(default=True)

    def __str__(self):
        return self.user_membership.user.username
