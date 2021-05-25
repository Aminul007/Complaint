from SuperAdmin.models import Ministry
# Create your views here.


def get_all_ministry(request):
    ministry = Ministry.objects.all()
    context = {
        'ministry': ministry
    }
    return context
