from django.contrib import messages
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.messages.views import SuccessMessageMixin
from django.http import HttpResponseRedirect
from django.shortcuts import render
from django.urls import reverse, reverse_lazy
from django.utils.translation import gettext as _
from django.views.generic import DeleteView, View
from django.views.generic.edit import FormView

from geogem.gui_messages import get_gui_messages
from word_bank.models import UserWord

from .forms import CustomUserCreationForm, CustomUserLoginForm
from .models import CustomUser
from .tokens import account_activation_token
from .utils import *


class IndexView(View):
    template_name = 'index.html'
    
    def get(self, request):
        context = {
            'gui_messages': get_gui_messages(['base', 'index']),
        }
        return render(request, self.template_name, context)


class SignUpView(FormView):
    template_name = 'accounts/signup.html'
    form_class = CustomUserCreationForm
    success_url = reverse_lazy('learn')
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['gui_messages'] = get_gui_messages(['base', 'accounts'])
        return context

    def form_valid(self, form):
        user = form.save(commit=False)
        user.save()
        user_token = CustomUserToken.objects.create(
            user=user, 
            token=account_activation_token.make_token(user)
        )
        if form.send_activation_email(self.request, user, user_token.token):
            success_message = GUI_MESSAGES['messages']['email_sent'].format(user=user, to_email=form.cleaned_data.get('email'))
            messages.success(self.request, success_message)
            
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
        return super().form_valid(form)


def logout_view(request):
    logout(request)
    return HttpResponseRedirect(reverse('index'))


class ProfileView(View):
    template_name = 'accounts/my_profile.html'
    
    def get(self, request):
        user = request.user
        if user.is_authenticated:
            user_profile = user.profile
            user_profile.num_learned_words = UserWord.objects.filter(user=request.user).count()
            
            context = {
                'gui_messages': get_gui_messages(['base', 'my_profile', 'tooltips']),
                'user_profile': user_profile
            }
            return render(request, self.template_name, context=context)

        return HttpResponseRedirect(reverse('login'))


class DeleteUserView(SuccessMessageMixin, DeleteView):
    model = CustomUser
    success_url = reverse_lazy('index')    
    success_message = GUI_MESSAGES['messages']['user_deleted']

    def form_valid(self, form):
        messages.success(self.request, self.success_message)
        return super().form_valid(form)


class PremiumView(View):
    template_name = 'word_bank/premium.html'

    def get(self, request):
        context = {
            'gui_messages': get_gui_messages(['base', 'premium']),
        }
        return render(request, self.template_name, context)


class GetPremiumView(LoginRequiredMixin, View):
    model = CustomUser

    def post(self, request):
        user = request.user
        if not user.is_premium:
            user.is_premium = True
            user.save()
        return HttpResponseRedirect(reverse('learn'))
    

class CancelPremiumView(View):
    model = CustomUser

    def post(self, request):
        user = request.user
        if user.is_authenticated:
            user.is_premium = False
            user.save()
        return HttpResponseRedirect(reverse('learn'))
