from django.shortcuts import render,redirect,reverse
from django.views.generic import TemplateView,ListView, CreateView,FormView
from django.core.files.storage import FileSystemStorage
from django.urls import reverse_lazy
from django.contrib.auth.models import User
from django.contrib.auth.forms import UserCreationForm
from django.contrib import messages
from django.contrib.auth import authenticate,login,logout
from django.contrib.auth.decorators import login_required,user_passes_test
import math
from django.core.mail import send_mail
from django.views import View 
import uuid
from django.utils.http import urlsafe_base64_encode, urlsafe_base64_decode
from django.core.mail import EmailMessage
from django.template.loader import get_template
from django.utils.encoding import force_bytes, force_text
from django.conf import settings

from .forms import DocumentForm,Document2Form,RegisterFrom
from .models import Document
from .tokens import user_tokenizer


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
    set_total_size_global(totalsize)
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
    elif totalsize>66 and totalsize<=95:
        progressbar_color="bg-warning"
    else:
        progressbar_color="bg-danger"
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
    global totalsize_global
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

@login_required
def upload_doc(request):
    if totalsize_global<1073741824:
        if request.method == 'POST':
            form = DocumentForm(request.POST,request.FILES)
            if form.is_valid():
                file=Document(source=request.FILES['source'])
                file.user=request.user
                file.title=file.filename
                file.validate_unique()
                file.clean_fields()
                if(file.size+totalsize_global>1073741824):
                    messages.error(request,'Not enough storage space!')
                else:
                    messages.success(request,'File uploaded successfully!')
                    file.save()
                return redirect('home')
        else:
            form=DocumentForm()
    else:
        return redirect('home')
    

    return render(request,'store/upload_doc.html',{
        'form':form
    })

def handle_chunk_upload(file):
    doc_model=Document(file)
    ext = file.name.split('.')[-1]
    filename = "%s.%s" % (uuid.uuid4(), ext)
    with open(f'media/{filename}','wb+') as destination:
        for chunk in file.chunks():
            destination.write(chunk)

class DocumentView(FormView):
    form_class=Document2Form
    template_name='store/upload.html'
    model=Document
    success_url= reverse_lazy('home')

    def post(self,request,*args,**kwargs):
        form_class=self.get_form_class()
        form=self.get_form(form_class)
        files=request.FILES.getlist('file_field')
        if form.is_valid():
            for file in files:
                print(type(file).__name__)
                for attributes in dir(file):
                    print(attributes)
                """ doc_model=Document(source=file)
                print(doc_model.filename+" "+doc_model.uploader+" "+doc_model.url) """
                #handle_chunk_upload(file)
            return self.form_valid(form)
        else:
            return self.form_invalid(form)

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

class RegisterView(View):
    def get(self, request):
        return render(request, 'signup.html', { 'form': RegisterFrom() })

    def post(self, request):
        form = RegisterFrom(request.POST)
        if form.is_valid():
            user = form.save(commit=False)
            user.is_valid = False
            user.save()
            token = user_tokenizer.make_token(user)
            user_id = urlsafe_base64_encode(force_bytes(user.id))
            url = 'http://localhost:8000' + reverse('confirm_email', kwargs={'user_id': user_id, 'token': token})
            message = get_template('signup_email.html').render({
              'confirm_url': url
            })
            mail = EmailMessage('EasyStore Account Confirmation', message, to=[user.email], from_email=settings.EMAIL_HOST_USER)
            mail.content_subtype = 'html'
            mail.send()
            messages.success(request,f'A confirmation email has been sent to {user.email}! Please confirm your account to finish the sign up process')
            return redirect('base_generic')
        else:
            form=RegisterFrom()
            messages.warning(request,'Registration failed!')

        return render(request, 'signup.html', { 'form': form })

class ConfirmRegistrationView(View):
    
    def get(self, request, user_id, token):
        context={}
        form=RegisterFrom()
        user_id = force_text(urlsafe_base64_decode(user_id))
        user = User.objects.get(pk=user_id)
        
        if user and user_tokenizer.check_token(user, token):
            user.is_valid = True
            user.save()
            messages.success(request,'Sign up complete! You can login now.')
            return redirect('base_generic')
        else:
            form=RegisterFrom()
            messages.warning(request,'Sign up failed!')
        context['form']=form
        return render(request,'signup.html',context)

        

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