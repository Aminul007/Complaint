from django.shortcuts import render
from SuperAdmin.models import Ministry
from .models import *
from .forms import *
from django.shortcuts import render, redirect, reverse
from django.contrib.auth.decorators import login_required


@login_required(login_url='log_in')
def create_complaint(request, complaint_id):
    complaint = Ministry.objects.get(id=complaint_id)
    form = ComplaintForms(instance=complaint)
    if request.method == "POST":
        form = ComplaintForms(request.POST or None, request.FILES or None)
        if form.is_valid():
            print('valid form')
            c = form.save(commit=False)
            c.username = request.user
            c.ministry_name = complaint
            c.save()
            return redirect(reverse('home'))

    if request.method == "GET":
        context = {
            'form': form,
            'complaint': complaint
        }
        return render(request, 'create_complaint.html', context=context)


def about(request):
    return render(request, 'about.html')


def service(request):
    return render(request, 'service.html')
