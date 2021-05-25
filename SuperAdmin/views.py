from django.contrib import messages
from django.contrib.auth.models import User
from django.shortcuts import render, redirect, get_object_or_404, reverse
from django.shortcuts import render, get_object_or_404
from django.http import JsonResponse
from django.template.loader import render_to_string
# Create your views here.
from .forms import MinistryForm, GovtSignUpForm, GovtSignUpUpdateForm, DistrictForm, PoliceStationForm, UNOSignUpForm, UnoSignUpUpdateForm
from .models import Ministry, District, PoliceStation
from django.shortcuts import render
from accounts.forms import UserUpdateForm, ChangeEmailForm
from django.views.generic import View, FormView
from django.conf import settings
from django.utils.crypto import get_random_string
from accounts.models import Activation
from django.contrib.auth import login, authenticate, REDIRECT_FIELD_NAME
from accounts.utils import (
    send_activation_email, send_reset_password_email, send_forgotten_username_email, send_activation_change_email,
)
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.auth.views import (
    LogoutView as BaseLogoutView, PasswordChangeView as BasePasswordChangeView,
    PasswordResetDoneView as BasePasswordResetDoneView, PasswordResetConfirmView as BasePasswordResetConfirmView,
)
from .filters import GovtUserFilter
from django.contrib.auth import get_user_model
User = get_user_model()


def SuperAdminHome(request):
    user = User.objects.all()
    complaint_problem = Ministry.objects.all().count()
    ministry_incharge = user.filter(is_ministry_incharge=True).count()
    context = {
        'ministry_incharge': ministry_incharge,
        'complaint_problem': complaint_problem,
    }
    return render(request, 'SuperAdmin/Home.html', context)


def SuperAdminProfile(request):
    if request.method == 'POST':
        u_form = UserUpdateForm(request.POST or None, request.FILES or None, instance=request.user)
        if u_form.is_valid():
            u_form.save()
            messages.success(request, f'Your account has been updated')
            return redirect('SuperAdminProfile')
    else:
        u_form = UserUpdateForm(instance=request.user)

    context = {
        'u_form': u_form
    }
    return render(request, 'SuperAdmin/Profile/SuperAdminProfile.html', context)


def ministry_list(request):
    ministry = Ministry.objects.all()
    context = {
        'ministrys': ministry
    }
    return render(request, 'SuperAdmin/Ministry/ministry_list.html', context=context)


def ministry_create(request):
    if request.method == 'POST':
        form = MinistryForm(request.POST or None)
        if form.is_valid():
            m = form.save(commit=False)
            m.username = request.user
            m.save()
            return redirect(reverse('ministry_list'))
    if request.method == "GET":
        form = MinistryForm()
        context = {
            'form': form
        }
        return render(request, 'SuperAdmin/Ministry/partial_ministry_create.html', context=context)


def ministry_update(request, pk):
    ministry = get_object_or_404(Ministry, pk=pk)
    if request.method == 'POST':
        form = MinistryForm(request.POST or None, instance=ministry)
        if form.is_valid():
            form.save()
            return redirect(reverse('ministry_list'))
    else:
        form = MinistryForm(instance=ministry)
        context = {
            'form': form
        }
        return render(request, 'SuperAdmin/Ministry/partial_ministry_update.html', context=context)


def ministry_delete(request, pk):
    ministry = get_object_or_404(Ministry, pk=pk)
    if request.method == 'POST':
        ministry.delete()
        return redirect(reverse('ministry_list'))
    context = {
        'ministry': ministry
    }
    return render(request, 'SuperAdmin/Ministry/partial_ministry_delete.html', context=context)


class GovtSignUpView(FormView):
    template_name = 'SuperAdmin/GovtEmployee/partial_employee_create.html'
    form_class = GovtSignUpForm

    def form_valid(self, form):
        request = self.request
        user = form.save(commit=False)

        if settings.DISABLE_USERNAME:
            # Set a temporary username
            user.username = get_random_string()
        else:
            user.username = form.cleaned_data['username']

        if settings.ENABLE_USER_ACTIVATION:
            user.is_active = False

        # Create a user record
        user.save()

        # Change the username to the "user_ID" form
        if settings.DISABLE_USERNAME:
            user.username = f'user_{user.id}'
            user.save()

        if settings.ENABLE_USER_ACTIVATION:
            code = get_random_string(20)

            act = Activation()
            act.code = code
            act.user = user
            act.save()

            send_activation_email(request,user.email, code)

            messages.success(request,f'Account is Created and You are signed up. To activate the account, follow the '
                                     f'link sent to the mail.')
        else:
            raw_password = form.cleaned_data['password1']

            user = authenticate(username=user.username, password=raw_password)
            login(request, user)
            messages.success(request,f'You are successfully signed up!')

        return redirect('employee_list')


def employee_list(request):
    employees = User.objects.all().filter(is_ministry_incharge=True)
    MyFilter = GovtUserFilter(request.GET, queryset=employees)
    employees = MyFilter.qs
    context = {
        'employees': employees,
        'MyFilter': MyFilter,
    }
    return render(request, 'SuperAdmin/GovtEmployee/employee_list.html', context)


def employee_update(request, pk):
    course = get_object_or_404(User, pk=pk)
    form = GovtSignUpUpdateForm(request.POST or None, request.FILES or None, instance=course)
    if form.is_valid():
        form.save()
        messages.success(request, "User Updated Successfully")
        return redirect("employee_list")
    # else:
    #     messages.error(request, "Training Not Updated Successfully")
    return render(request, 'SuperAdmin/GovtEmployee/partial_employee_update.html', {'form': form})


def employee_delete(request, pk):
    employee = get_object_or_404(User, pk=pk)
    if request.method == 'POST':
        employee.delete()
        return redirect(reverse("employee_list"))
    context = {
        'employee': employee
    }
    return render(request, 'SuperAdmin/GovtEmployee/partial_employee_delete.html', context=context)


def employee_view(request, pk):
    employee = get_object_or_404(User, pk=pk)
    context = {
        'employee': employee
    }
    return render(request, 'SuperAdmin/GovtEmployee/partial_employee_view.html', context=context)


class ChangeEmailView(LoginRequiredMixin, FormView):
    template_name = 'SuperAdmin/Profile/change_email.html'
    form_class = ChangeEmailForm

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs['user'] = self.request.user
        return kwargs

    def get_initial(self):
        initial = super().get_initial()
        initial['email'] = self.request.user.email
        return initial

    def form_valid(self, form):
        user = self.request.user
        email = form.cleaned_data['email']

        if settings.ENABLE_ACTIVATION_AFTER_EMAIL_CHANGE:
            code = get_random_string(20)

            act = Activation()
            act.code = code
            act.user = user
            act.email = email
            act.save()

            send_activation_change_email(self.request, email, code)

            messages.success(self.request, f'To complete the change of email address, click on the link sent to it.')
        else:
            user.email = email
            user.save()

            messages.success(self.request, f'Email successfully changed.')

        return redirect('SuperAdmin_change_email')


class ChangeEmailActivateView(View):
    @staticmethod
    def get(request, code):
        act = get_object_or_404(Activation, code=code)

        # Change the email
        user = act.user
        user.email = act.email
        user.save()

        # Remove the activation record
        act.delete()

        messages.success(request, f'You have successfully changed your email!')

        return redirect('SuperAdmin_change_email')


class ChangePasswordView(BasePasswordChangeView):
    template_name = 'SuperAdmin/Profile/change_password.html'

    def form_valid(self, form):
        # Change the password
        user = form.save()

        # Re-authentication
        login(self.request, user)

        messages.success(self.request, f'Your password was changed.')

        return redirect('log_in')


def district_list(request):
    district = District.objects.all()
    context = {
        'district': district
    }
    return render(request, 'SuperAdmin/District/district_list.html', context=context)


def district_create(request):
    form = DistrictForm()
    if request.method == 'POST':
        form = DistrictForm(request.POST or None)
        if form.is_valid():
            form.save()
            return redirect(reverse('district_list'))
    context = {
        'form': form
    }
    return render(request, 'SuperAdmin/District/partial_district_create.html', context=context)


def district_update(request, pk):
    district = get_object_or_404(District, pk=pk)
    if request.method == 'POST':
        form = DistrictForm(request.POST or None, instance=district)
        if form.is_valid():
            form.save()
            return redirect(reverse('district_list'))
    else:
        form = DistrictForm(instance=district)
        context = {
            'form': form
        }
        return render(request, 'SuperAdmin/District/partial_district_update.html', context=context)


def district_delete(request, pk):
    district = get_object_or_404(District, pk=pk)
    if request.method == 'POST':
        district.delete()
        return redirect(reverse('district_list'))
    context = {
        'district': district
    }
    return render(request, 'SuperAdmin/District/partial_district_delete.html', context=context)


def police_list(request):
    police = PoliceStation.objects.all()
    context = {
        'police': police
    }
    return render(request, 'SuperAdmin/Police/police_list.html', context=context)


def police_create(request):
    form = PoliceStationForm()
    if request.method == 'POST':
        form = PoliceStationForm(request.POST or None)
        if form.is_valid():
            form.save()
            return redirect(reverse('police_list'))
    context = {
        'form': form
    }
    return render(request, 'SuperAdmin/Police/partial_police_create.html', context=context)


def police_update(request, pk):
    police = get_object_or_404(PoliceStation, pk=pk)
    if request.method == 'POST':
        form = PoliceStationForm(request.POST or None, instance=police)
        if form.is_valid():
            form.save()
            return redirect(reverse('police_list'))
    else:
        form = PoliceStationForm(instance=police)
        context = {
            'form': form
        }
        return render(request, 'SuperAdmin/Police/partial_police_update.html', context=context)


def police_delete(request, pk):
    police = get_object_or_404(PoliceStation, pk=pk)
    if request.method == 'POST':
        police.delete()
        return redirect(reverse('police_list'))
    context = {
        'police': police
    }
    return render(request, 'SuperAdmin/Police/partial_police_delete.html', context=context)


class UnoSignUpView(FormView):
    template_name = 'SuperAdmin/Uno/partial_uno_create.html'
    form_class = UNOSignUpForm

    def form_valid(self, form):
        request = self.request
        user = form.save(commit=False)

        if settings.DISABLE_USERNAME:
            # Set a temporary username
            user.username = get_random_string()
        else:
            user.username = form.cleaned_data['username']

        if settings.ENABLE_USER_ACTIVATION:
            user.is_active = False

        # Create a user record
        user.save()

        # Change the username to the "user_ID" form
        if settings.DISABLE_USERNAME:
            user.username = f'user_{user.id}'
            user.save()

        if settings.ENABLE_USER_ACTIVATION:
            code = get_random_string(20)

            act = Activation()
            act.code = code
            act.user = user
            act.save()

            send_activation_email(request, user.email, code)

            messages.success(request, f'Account is Created and You are signed up. To activate the account, follow the '
                                      f'link sent to the mail.')
        else:
            raw_password = form.cleaned_data['password1']

            user = authenticate(username=user.username, password=raw_password)
            login(request, user)
            messages.success(request, f'You are successfully signed up!')

        return redirect('uno_list')


def uno_list(request):
    uno = User.objects.all().filter(is_uno=True)
    context = {
        'uno': uno,
    }
    return render(request, 'SuperAdmin/Uno/uno_list.html', context)


def uno_update(request, pk):
    uno = get_object_or_404(User, pk=pk)
    form = UnoSignUpUpdateForm(request.POST or None, request.FILES or None, instance=uno)
    if form.is_valid():
        form.save()
        messages.success(request, "User Updated Successfully")
        return redirect("uno_list")
    # else:
    #     messages.error(request, "Training Not Updated Successfully")
    return render(request, 'SuperAdmin/Uno/partial_unp_update.html', {'form': form})


def uno_delete(request, pk):
    uno = get_object_or_404(User, pk=pk)
    if request.method == 'POST':
        uno.delete()
        return redirect(reverse("uno_list"))
    context = {
        'uno': uno
    }
    return render(request, 'SuperAdmin/Uno/partial_uno_delete.html', context=context)


def uno_view(request, pk):
    uno = get_object_or_404(User, pk=pk)
    context = {
        'uno': uno
    }
    return render(request, 'SuperAdmin/Uno/partial_uno_view.html', context=context)
