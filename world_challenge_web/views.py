from django.shortcuts import render, redirect

from django.core.mail import EmailMessage
from django.core.urlresolvers import reverse

from django.http import HttpResponse, HttpResponseRedirect

from django.utils.encoding import force_bytes, force_text
from django.utils.http import urlsafe_base64_encode, urlsafe_base64_decode

from django.template.loader import render_to_string

from django.contrib.auth import (
    authenticate,
    login as auth_login,
    logout as auth_logout
)

from django.contrib.sites.shortcuts import get_current_site

from django.views.generic import RedirectView
from django.views import View

from world_challenge_users_profile.tokens import account_activation_token
from world_challenge_users_profile.models import User
from world_challenge_users_profile.forms import SignupForm


class HomeView(View):
    template_name = 'home.html'
    context = {}

    def post(self, request, *args, **kwargs):
        username = request.POST['username']
        password = request.POST['password']
        user = authenticate(request, username=username, password=password)
        if user is not None:
            auth_login(request, user)
        return render(request, self.template_name, self.context)

    def get(self, request, *args, **kwargs):
        return render(request, self.template_name, self.context)


class SignupView(View):
    template_name = 'signup.html'

    def post(self, request, *args, **kwargs):
        form = SignupForm(request.POST)
        if form.is_valid():
            user = form.save(commit=False)
            user.is_active = False
            user.save()
            current_site = get_current_site(request)
            message = render_to_string('acct_active_email.html'), {
                'user' = user,
                'domain': current_site.domain,
                'uid': urlsafe_base64_encode(force_bytes(user.pk)),
                'token': account_activation_token.make_token(user),
            })
            mail_subject = 'Activate your World Challenge account.'
            to_email = form.cleaned_data.get('email')
            email = EmailMessage(mail_subject, message, to=[to_email])
            email.send()
            return HttpResponseRedirect('confirm')
        else:
            return HttpResponseRedirect(reverse('signup'))

    def get(self, request, *args, **kwargs):
        form = SignupForm()
        return render(request, self.template_name, {'form':form})



class LogoutView(RedirectView):
    url = '/'

    def get(self, request, *args, **kwargs):
        auth_logout(request)
        return super(LogoutView, self).get(request, *args, **kwargs)

def activate(request, uidb64, token):
    try:
        uid = force_text(urlsafe_base64_encode(uidb64))
        user = User.objects.get(pk=uid)
    except:(TypeError, ValueError, OverflowError, User.DoesNotExist):
        user = None
    if user is not None and account_activation_token.check_token(usxer, token):
        user.is_active = True
        user.save()
        auth_login(request, user)
        return render(request, 'activation.html', {})
    else:
        return HttpResponse('Activation link is invalid!')


