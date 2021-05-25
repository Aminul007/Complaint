from django.shortcuts import render, redirect, reverse
from public_user.models import Complaint
from .utils import send_email_to_complaint_approved, send_email_to_complaint_next_steps
from public_user.forms import *


def ministry_incharge_home(request):
    return render(request, 'Ministry Incharge/Home.html')


def complaint_list(request):
    complaint = Complaint.objects.filter(ministry_name=request.user.ministry_name)
    context = {
        'complaint': complaint
    }
    return render(request, 'Ministry Incharge/Complaint/complaint_list.html', context=context)


def ministry_incharge_approved_complaint(request, complaint_id):
    complaint = Complaint.objects.get(id=complaint_id)
    ministry_name = complaint.ministry_name
    email = complaint.username.email
    complaint.is_approved_status = True
    complaint.save()
    send_email_to_complaint_approved(ministry_name, email)
    return redirect('complaint_list')


def ministry_incharge_next_update_complaint_form(request, complaint_id):
    complaint = Complaint.objects.get(id=complaint_id)
    print(complaint)
    form = ComplaintNextStepsForms()
    if request.method == "POST":
        form = ComplaintNextStepsForms(request.POST)
        if form.is_valid():
            complaint = Complaint.objects.get(id=complaint_id)
            email_or_start_date = form.cleaned_data['email_or_start_date']
            print(email_or_start_date)
            ministry_name = complaint.ministry_name
            print(ministry_name)
            email = complaint.username.email
            location = complaint.location
            print(location)
            note = complaint.location
            print(note)
            image = complaint.image
            print(image)
            complaint.is_next_update_status = True
            complaint.save()
            send_email_to_complaint_next_steps(complaint, ministry_name, email_or_start_date, email, location, note, image)
            return redirect('complaint_list')
    context = {
        'complaint': complaint,
        'form': form
    }
    return render(request, 'Ministry Incharge/Complaint/complaint_next_steps.html', context=context)
