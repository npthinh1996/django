from django.shortcuts import render, reverse, redirect, HttpResponseRedirect
from django.contrib import messages
from django.conf import settings
from django.views.generic import ListView
import stripe
from .models import Membership, UserMembership, Subscription

def get_user_membership(request):
    user_membership_qs = UserMembership.objects.filter(user=request.user)
    if user_membership_qs.exists():
        return user_membership_qs.first()
    return None

def get_user_subscription(request):
    user_subscription_qs = Subscription.objects.filter(user_membership=get_user_membership(request))
    if user_subscription_qs.exists():
        return user_subscription_qs.first()
    return None

def get_selected_membership(request):
    membership_type = request.session['selected_membership_type']
    selected_membership_qs = Membership.objects.filter(
        membership_type=membership_type
    )
    if selected_membership_qs.exists():
        return selected_membership_qs.first()
    return None

class MembershipSelectView(ListView):
    model = Membership

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        current_membership = get_user_membership(self.request)
        context['current_membership'] = str(current_membership.membership)
        return context

    def post(self, request):
        user_membership = get_user_membership(request)
        user_subscription = get_user_subscription(request)
        selected_membership_qs = Membership.objects.filter(
            membership_type=request.POST['membership_type']
        )
        selected_membership = selected_membership_qs.first()

        if user_membership.membership == selected_membership:
            if user_subscription is not None:
                messages.info(request, """You already have this membership.
                Your next payment is due get this value from stripe""")
                return HttpResponseRedirect(request.META['HTTP_REFERER'])
        request.session['selected_membership_type'] = selected_membership.membership_type
        return HttpResponseRedirect(reverse('memberships:payment'))

def paymentView(request):
    user_membership = get_user_membership(request)
    selected_membership = get_selected_membership(request)
    publishKey = settings.STRIPE_PUBLISHABLE_KEY

    if request.method == 'POST':
        try:
            token = request.POST['stripeToken']
            cus = stripe.Customer.retrieve(user_membership.stripe_customer_id)
            cus.source = token
            cus.save()
            subscription = stripe.Subscription.create(
                customer=user_membership.stripe_customer_id,
                items=[{
                    'plan': selected_membership.stripe_plan_id
                }]
            )
            return redirect(reverse('memberships:update-transactions', kwargs={
                'sub_id': subscription.id
            }))
        except stripe.error.CardError:
            messages.info(request, 'Your card has been declined')

    context = {
        'publishKey': publishKey,
        'selected_membership': selected_membership
    }
    return render(request, 'memberships/membership_payment.html', context)

def updateTransactions(request, sub_id):
    user_membership = get_user_membership(request)
    selected_membership = get_selected_membership(request)
    user_membership.membership = selected_membership
    user_membership.save()

    sub = Subscription.objects.get_or_create(user_membership=user_membership)[0]
    sub.stripe_subscription_id = sub_id
    sub.active = True
    sub.save()

    try:
        del request.session['selected_membership_type']
    except KeyError:
        pass

    messages.info(request, f'Successfully created {selected_membership} membership')
    return redirect(reverse('memberships:select'))

def profileView(request):
    user_membership = get_user_membership(request)
    user_subscription = get_user_subscription(request)
    context = {
        'user_membership': user_membership,
        'user_subscription': user_subscription
    }
    return render(request, 'memberships/profile.html', context)

def cancelSubscription(request):
    user_sub = get_user_subscription(request)
    if user_sub.active is False:
        messages.info(request, 'You dont have an active membership')
        return HttpResponseRedirect(request.META['HTTP_REFERER'])
    sub = stripe.Subscription.retrieve(user_sub.stripe_subscription_id)
    sub.delete()

    user_sub.active = False
    user_sub.save()

    free_membership = Membership.objects.filter(membership_type='Free').first()
    user_membership = get_user_membership(request)
    user_membership.membership = free_membership
    user_membership.save()

    messages.info(request, 'Successfully cancelled membership. We have sent an email')
    return redirect(reverse('memberships:select'))
