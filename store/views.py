from django.shortcuts import render,redirect
from django.views.generic import TemplateView,ListView, CreateView
from django.core.files.storage import FileSystemStorage
from django.urls import reverse_lazy
from .forms import DocumentForm,RegisterFrom
from .models import Document
from django.contrib.auth.forms import UserCreationForm
from django.contrib import messages
from django.contrib.auth import authenticate,login,logout
from django.contrib.auth.decorators import login_required,user_passes_test
import math
from django.core.mail import send_mail

totalsize_global=0

""" def email_check(user):
    return user.id.equals('') """

@login_required
#@user_passes_test(email_check)
def home(request):
    num_visists = request.session.get('num_visits',0)
    request.session['num_visits']=num_visists+1
    docs=Document.objects.filter(user=request.user)
    user_folder=f'user_{request.user.id}'
    totalsize=get_total_size(docs)
    set_total_size_global(totalsize_global)
    totalsize_bytes=totalsize
    totalsize=totalsize/10000000
    totalsize_ceil=totalsize*100
    totalsize_ceil=math.ceil(totalsize_ceil)
    totalsize_ceil=totalsize_ceil/100
    progressbar_color=""
    if totalsize<=33:
        progressbar_color="bg-success"
    elif totalsize>33 and totalsize<=66:
        progressbar_color="bg-info"
    elif totalsize>66 and totalsize<=99:
        progressbar_color="bg-warning"
    else:
        progressbar_color="bg-danger"
    print(totalsize_bytes)
    if totalsize_bytes>1073741824:
        upload_available=False
    else:
        upload_available=True
    
    
    context = {
        'num_visits':num_visists,
        'docs':docs,
        'totalsize':totalsize,
        'totalsize_ceil':totalsize_ceil,
        'progressbar_color':progressbar_color,
        'upload_available':upload_available,
        'user_folder':user_folder,
    }
    
    return render(request,'base_home.html',context=context)

def set_total_size_global(size):
    totalsize_global=size

def get_total_size(docs):
    totalsize=0
    for doc in docs:
        totalsize += doc.source.size
    return totalsize

def index(request):
    context={}
    return render(request,'login.html',context)

def upload(request):
    context={}
    if request.method=='POST':
        uploaded_file=request.FILES['doc']
        print(uploaded_file.name)
        print(uploaded_file.size)
        print(request.user.pk)
        fs=FileSystemStorage()
        path=f"uploads/{request.user.pk}"
        print(path)
        fs.location=path
        name=fs.save(uploaded_file.name,uploaded_file)
        print(name)
        url_path=path+"/"+name
        print(url_path)
        fs.url(url_path)
        #context['url']=fs.url(url_path)
        context['url']=url_path
    return render(request,'store/upload.html',context)

# de refactorizat
def docs_list(request):
    docs=Document.objects.filter(user=request.user)
    
    
    return render(request, 'store/doc_list.html',{
        'docs':docs,
    })


def upload_doc(request):
    if request.method == 'POST':
        form = DocumentForm(request.POST,request.FILES)
        if form.is_valid():
            file=Document(source=request.FILES['source'])
            file.user=request.user
            file.save()
            return redirect('home')
    else:
        form=DocumentForm()

    return render(request,'store/upload_doc.html',{
        'form':form
    })

def delete_doc(request,pk):
    if request.method=='POST':
        doc=Document.objects.get(pk=pk)
        doc.delete()
    return redirect('home')

class DocsListView(ListView):
    model = Document
    template_name='store/class_docs_list.html'
    context_object_name='docs'

class UploadCreateView(CreateView):
    model= Document
    form_class=DocumentForm
    success_url=reverse_lazy('class_docs_list')
    template_name='store/upload_doc.html'

def loginUser(request):
    context={}
    if request.method == 'POST':
        username=request.POST.get('username')
        password=request.POST.get('password')

        user=authenticate(request,username=username,password=password)

        if user is not None:
            login(request,user)
            return redirect('home')
        else:
            messages.info(request,'Username or password is incorrect!')
    return render(request,'login.html',context)

def logoutUser(request):
    logout(request)
    return redirect('base_generic')

def register(request):
    context={}
    form=RegisterFrom()
    if request.method=='POST':
        form=RegisterFrom(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request,'Account created successfully!')
            return redirect('base_generic')
        else:
            form=RegisterFrom()
            messages.warning(request,'Registration failed!')
    context['form']=form
    return render(request,'signup.html',context)

def percent_available(request):
    context={}

def send():
    send_mail('test ','mesaj de test','uraresgaming@gmail.com',['urares31@gmail.com'])



""" def activate_account(request, uidb64, token):
    try:
        uid=force_text(urlsafe_base64_decode(uidb64))
        user= User.objects.get(pk=uid)
    except(TypeError,ValueError,OverflowError,User.DoesNotExist):
        user= None
    if user is not None and account_activation_token.check_token(user,token):
        user.is_active= True
        user.save()
        login(request,user)
        return HttpResponse('Thank you for registering to EasyStore! You can now login to your account.')
    else:
        return HttpResponse('Activation failed!') """