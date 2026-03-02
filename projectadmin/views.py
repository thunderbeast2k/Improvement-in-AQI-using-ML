from django.shortcuts import render,redirect

# Create your views here.
from projectadmin.models import DatatrainModel


def admin_login(request):
    if request.method == "POST":
        uname = request.POST.get("uname")
        password = request.POST.get("password")
        try:
            if uname == 'admin' and password == 'admin':
                return redirect("admin_home")
        except:
            pass
        return redirect('admin_login')
    return render(request, 'projectadmin/admin_login.html')

def admin_home(request):
    myfile = ''
    a = ''
    b = ''
    c = ''
    d = ''
    e = ''
    f = ''
    if request.method == "POST" and request.FILES['myfile']:
        myfile = request.FILES['myfile']
        a = request.POST.get('air_quality')
        b = request.POST.get('prediction')


        DatatrainModel.objects.create(img=myfile, air_quality=a, predictionvalue=b)
    return render(request, 'projectadmin/admin_home.html')