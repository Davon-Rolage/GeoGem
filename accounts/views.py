from django.contrib import messages
from django.contrib.auth import authenticate, get_user_model, login, logout
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.auth.tokens import PasswordResetTokenGenerator
from django.contrib.messages.views import SuccessMessageMixin
from django.http import HttpResponseRedirect
from django.shortcuts import render
from django.urls import reverse, reverse_lazy
from django.utils.translation import gettext as _
from django.views.generic import DeleteView, RedirectView, View
from django.views.generic.base import TemplateView
from django.views.generic.edit import FormView

from geogem.gui_messages import get_gui_messages

from .forms import *
from .models import CustomUserTokenType
from .tokens import generate_user_token
from .utils import *


class IndexView(TemplateView):
    template_name = 'index.html'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['gui_messages'] = get_gui_messages(['base', 'index'])
        return context


class SignUpView(FormView):
    template_name = 'accounts/signup.html'
    form_class = CustomUserCreationForm
    success_url = reverse_lazy('learn')
    token_type = CustomUserTokenType.objects.get(name='User activation')
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['gui_messages'] = get_gui_messages(['base', 'accounts'])
        return context
    
    def form_valid(self, form):
        user = form.save(commit=False)
        user.save()
        email = form.cleaned_data.get('email')
        CustomUserToken.objects.create(
            user=user,
            token=generate_user_token(user.id),
            token_type=self.token_type,
        )
        domain = self.request.get_host()
        protocol = self.request.scheme
        form.send_activation_email( # pragma: no cover
            user_id=user.id,
            domain=domain,
            protocol=protocol,
            to_email=email,
        )
        success_message = GUI_MESSAGES['messages']['activation_email_sent'].format(
            user=user, to_email=email
        )
        messages.success(self.request, success_message) # pragma: no cover
        return super().form_valid(form)


class LoginView(FormView):
    template_name = 'accounts/login.html'
    form_class = CustomUserLoginForm
    success_url = reverse_lazy('learn')
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['gui_messages'] = get_gui_messages(['base', 'accounts'])
        return context
    
    def form_valid(self, form):
        username = form.cleaned_data.get('username')
        password = form.cleaned_data.get('password')
        login(self.request, authenticate(username=username, password=password))
        
        stay_signed_in = form.cleaned_data.get('stay_signed_in')
        if stay_signed_in:
            self.request.session.set_expiry(None) # default 14 days
        else:
            self.request.session.set_expiry(0) # until browser is closed
            # Some browsers, like Chrome, can interfere with session expiration on browser close:
            # https://docs.djangoproject.com/en/4.2/topics/http/sessions/#browser-length-sessions-vs-persistent-sessions
        return super().form_valid(form)


def logout_view(request):
    logout(request)
    return HttpResponseRedirect(reverse('index'))


class ProfileView(LoginRequiredMixin, View):
    template_name = 'accounts/profile.html'
    
    def get(self, request):
        user = request.user
        user_profile = user.profile        
        context = {
            'gui_messages': get_gui_messages(['base', 'my_profile', 'tooltips']),
            'user_profile': user_profile
        }
        return render(request, self.template_name, context=context)


class DeleteUserView(SuccessMessageMixin, DeleteView):
    model = get_user_model()
    success_url = reverse_lazy('index')    
    success_message = GUI_MESSAGES['messages']['user_deleted']

    def form_valid(self, form):
        messages.success(self.request, self.success_message)
        return super().form_valid(form)


class PasswordResetView(FormView):
    template_name = 'accounts/password_reset.html'
    form_class = PasswordResetForm
    success_url = reverse_lazy('learn')
    token_generator = PasswordResetTokenGenerator()
    token_type = CustomUserTokenType.objects.get(name='Password reset')
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['gui_messages'] = get_gui_messages(['base', 'accounts'])
        return context
    
    def form_valid(self, form):
        email = form.cleaned_data.get('email')
        user = get_user_model().objects.get(email=email)
        CustomUserToken.objects.filter(
            user=user,
            token_type=self.token_type
        ).delete()
        CustomUserToken.objects.create(
            user=user,
            token=self.token_generator.make_token(user),
            token_type=self.token_type,
        )
        domain = self.request.get_host()
        protocol = self.request.scheme
        form.send_password_reset_email( # pragma: no cover
            user_id=user.id,
            domain=domain,
            protocol=protocol,
            to_email=email,
        )
        success_message = GUI_MESSAGES['messages']['password_reset_email_sent'].format(
            to_email=email
        )
        messages.success(self.request, success_message) # pragma: no cover
        return super().form_valid(form)


class PasswordResetCheckView(RedirectView):
    token_generator = PasswordResetTokenGenerator()

    def get_redirect_url(self, token):
        try:
            user_token = CustomUserToken.objects.get(token=token)
            user = user_token.user

        except (ValueError, CustomUserToken.DoesNotExist):
            messages.error(self.request, GUI_MESSAGES['error_messages']['password_reset_failed'])
            user = None

        except signing.BadSignature:
            messages.error(self.request, GUI_MESSAGES['error_messages']['password_reset_failed'])
            user_token.delete()
            user = None

        if user is not None and self.token_generator.check_token(user, token):
            return reverse('set_password', args=[token])

        return reverse('login')


class SetPasswordView(FormView):
    template_name = 'accounts/password_set.html'
    form_class = SetPasswordForm
    success_url = reverse_lazy('login')
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['gui_messages'] = get_gui_messages(['base', 'accounts'])
        return context
    
    def form_valid(self, form):
        token = self.kwargs.get('token')
        token_instance = CustomUserToken.objects.get(token=token)
        user = token_instance.user
        
        user.set_password(form.cleaned_data.get('password1'))
        user.save()
        
        messages.success(self.request, GUI_MESSAGES['messages']['password_reset_successful'])
        token_instance.delete()
        return super().form_valid(form)


class PremiumView(View):
    template_name = 'word_bank/premium.html'

    def get(self, request):
        context = {
            'gui_messages': get_gui_messages(['base', 'premium']),
        }
        return render(request, self.template_name, context)


class GetPremiumView(LoginRequiredMixin, View):
    model = get_user_model()

    def post(self, request):
        user = request.user
        if not user.is_premium:
            user.is_premium = True
            user.save()
        return HttpResponseRedirect(reverse('learn'))
    

class CancelPremiumView(View):
    model = get_user_model()

    def post(self, request):
        user = request.user
        if user.is_authenticated:
            user.is_premium = False
            user.save()
        return HttpResponseRedirect(reverse('learn'))
