from django.contrib import messages
from django.contrib.auth import authenticate, login, logout
from django.contrib.messages.views import SuccessMessageMixin
from django.http import HttpResponseRedirect
from django.shortcuts import render
from django.urls import reverse, reverse_lazy
from django.utils.translation import gettext as _
from django.views.generic import DeleteView, View

from accounts.models import MyProfile
from geogem.gui_messages import get_gui_messages
from word_bank.models import UserWord

from .forms import CustomUserCreationForm, CustomUserLoginForm
from .models import CustomUser
from .tokens import account_activation_token
from .utils import *


class IndexView(View):
    template_name = 'index.html'
    gui_messages = get_gui_messages(['base', 'index'])
    
    def get(self, request):
        context = {
            'gui_messages': self.gui_messages,
        }
        return render(request, self.template_name, context)


class SignUpView(View):
    template_name = 'accounts/signup.html'
    form_class = CustomUserCreationForm
    gui_messages = get_gui_messages(['base', 'accounts'])
        
    def get(self, request):
        form = self.form_class()
        context = {
            'gui_messages': self.gui_messages,
            'form': form
        }
        return render(request, self.template_name, context)
    
    def post(self, request):
        form = self.form_class(request.POST)
        if form.is_valid():
            user = form.save(commit=False)
            user.save()
            if not user.is_active:
                user_token = CustomUserToken.objects.create(
                    user=user, 
                    token=account_activation_token.make_token(user)
                )
                send_activation_email(request, user, user_token.token, form.cleaned_data.get('email'))
            return HttpResponseRedirect(reverse('index'))

        context = {
            'gui_messages': self.gui_messages,
            'form': form
        }
        return render(request, self.template_name, context)


class LoginView(View):
    template_name = 'accounts/login.html'
    gui_messages = get_gui_messages(['base', 'accounts'])
    
    def get(self, request):
        form = CustomUserLoginForm()
        context = {
            'gui_messages': self.gui_messages,
            'form': form
        }
        return render(request, self.template_name, context)
    
    def post(self, request):
        form = CustomUserLoginForm(request.POST)
        if form.is_valid():
            username = form.cleaned_data.get('username')
            password = form.cleaned_data.get('password')
            login(request, authenticate(username=username, password=password))
            return HttpResponseRedirect(reverse('index'))
            
        context = {
            'gui_messages': self.gui_messages,
            'form': form
        }
        return render(request, self.template_name, context)


def logout_view(request):
    logout(request)
    return HttpResponseRedirect(reverse('index'))


class MyProfileView(View):
    template_name = 'accounts/my_profile.html'
    gui_messages = get_gui_messages(['base', 'my_profile', 'tooltips'])
    
    def get(self, request):
        user = request.user
        if user.is_authenticated:
            user_profile = user.profile
            user_profile.num_learned_words = UserWord.objects.filter(user=request.user).count()
            
            context = {
                'gui_messages': self.gui_messages,
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
    gui_messages = get_gui_messages(['base', 'premium'])

    def get(self, request):
        context = {
            'gui_messages': self.gui_messages,
        }
        return render(request, self.template_name, context)


class GetPremiumView(View):
    model = CustomUser

    def post(self, request):
        user = request.user
        if user.is_authenticated:
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
