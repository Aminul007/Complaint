from django.conf import settings
from django.core.mail import EmailMultiAlternatives
from django.template.loader import render_to_string
from django.urls import reverse
from django.utils.translation import gettext_lazy as _


def send_mail(to, template, context):
    html_content = render_to_string(f'Ministry Incharge/emails/{template}.html', context)
    text_content = render_to_string(f'Ministry Incharge/emails/{template}.txt', context)

    msg = EmailMultiAlternatives(context['subject'], text_content, settings.DEFAULT_FROM_EMAIL, [to])
    msg.attach_alternative(html_content, 'text/html')
    msg.send()


def send_email_to_complaint_approved(ministry_name, email):
    context = {
        'subject': 'Approved ' + str(ministry_name) + ' Complaint',
    }
    print(context)
    send_mail(email, 'complaint_email', context)


def send_email_to_complaint_next_steps(complaint, ministry_name, email_or_start_date, email, location, note, image):
    context = {
        'subject': 'Your Complaint Update ' + str(ministry_name) + ' Complaint',
        'complaint_name': complaint,
        'ministry_name': ministry_name,
        'email_or_start_date': email_or_start_date,
        'email': email,
        'location': location,
        'note': note,
        'image': image,
    }
    send_mail(email_or_start_date, 'complaint_to_thana', context)
