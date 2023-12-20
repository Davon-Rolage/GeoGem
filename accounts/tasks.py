from celery import shared_task
from django.contrib.auth import get_user_model
from django.core.mail import send_mail
from django.core.management import call_command
from django.template.loader import render_to_string

from geogem.gui_messages import GUI_MESSAGES

from .models import CustomUserToken


@shared_task
def send_activation_email_task(user_id=None, domain=None, protocol=None, to_email=None):
    mail_subject = GUI_MESSAGES['messages']['email_subject']
    user = get_user_model().objects.get(id=user_id)
    user_token = CustomUserToken.objects.get(user=user).token

    message = render_to_string('accounts/activate_email.html', {
        'username': user.get_username(),
        'domain': domain,
        'token': user_token,
        'protocol': protocol
    })
    send_mail(
        mail_subject, message, html_message=message,
        from_email=None, recipient_list=[to_email]
    )
    

@shared_task
def delete_expired_tokens_task():
    call_command('delete_expired_tokens')


@shared_task
def clean_out_expired_sessions_task():
    call_command('clearsessions')
