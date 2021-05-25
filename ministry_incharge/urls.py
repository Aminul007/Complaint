from django.urls import path

from ministry_incharge import views

urlpatterns = [
    path('home/', views.ministry_incharge_home, name='ministry_incharge_home'),
    path('complaint/list/', views.complaint_list, name='complaint_list'),
    path('ministry_incharge_approved_complaint/<int:complaint_id>/', views.ministry_incharge_approved_complaint,
         name='ministry_incharge_approved_complaint'),
    path('ministry_incharge_next_update_complaint_form/<int:complaint_id>/',
         views.ministry_incharge_next_update_complaint_form,
         name='ministry_incharge_next_update_complaint_form'),

]
