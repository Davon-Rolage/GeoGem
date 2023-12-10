from django.contrib import messages
from django.contrib.sites.shortcuts import get_current_site
from django.core.mail import send_mail
from django.http import (HttpResponse, HttpResponseNotAllowed,
                         HttpResponseRedirect, JsonResponse)
from django.template.loader import render_to_string
from django.urls import reverse
from django.views.generic import View

from accounts.models import CustomUserToken
from geogem.gui_messages import GUI_MESSAGES

from .models import CustomUser


def check_username_exists(request):
    if request.method == 'GET':
        username = request.GET.get('username').strip()
        if username:
            exists = CustomUser.objects.filter(username=username).exists()
            return JsonResponse({'exists': exists})
        else:
            return HttpResponse(status=204)

    return HttpResponseNotAllowed(['GET'])
    
    
class ActivateUserView(View):
    
    def get(self, request, *args, **kwargs):
        token = kwargs.get('token')
        try:
            user_token_instance = CustomUserToken.objects.get(token=token)
            user = user_token_instance.user
            if not user_token_instance.is_expired:
                user.is_active = True
                user.save()
                user_token_instance.delete()
                messages.success(request, GUI_MESSAGES['messages']['activation_successful'])
                return HttpResponseRedirect(reverse('login'))
            else:
                user_token_instance.delete()
        
        except CustomUserToken.DoesNotExist:
            pass
            
        messages.error(request, GUI_MESSAGES['error_messages']['activation_failed'])
        return HttpResponseRedirect(reverse('signup'))
    

def send_activation_email(request=None, user=None, user_token=None, to_email=None):
    mail_subject = GUI_MESSAGES['messages']['email_subject']
    try:
        message = render_to_string('accounts/activate_email.html', {
            'username': user.username,
            'domain': get_current_site(request).domain,
            'token': user_token,
            'protocol': 'https' if request.is_secure() else 'http'
        })
    except:
        message = render_to_string('accounts/activate_email.html', {
            'username': 'test_user',
            'domain': 'test_domain',
            'token': 'test_token',
            'protocol': 'test_protocol'
        })
    email = send_mail(mail_subject, message, html_message=message, from_email=None, recipient_list=[to_email])
    if email:
        if all([request, user, email]):
            success_message = GUI_MESSAGES['messages']['email_sent'].format(user=user, to_email=to_email)
            messages.success(request, success_message)
        return True
    else:
        messages.error(request, GUI_MESSAGES['error_messages']['email_sent'].format(to_email=to_email))
        return False
