from django.contrib import admin
from django.urls import path,include
from django.views.generic import RedirectView
from django.conf import settings
from django.conf.urls.static import static

urlpatterns = [
    path('admin/', admin.site.urls),
    path('store/', include('store.urls')),
    path('', RedirectView.as_view(url='store/', permanent=True)),
    #path('accounts/',include('django_registration.backends.activation.urls')),
    #path('accounts/',include('django.contrib.auth.urls')),
    path('accounts/',include('accounts.urls')),
    
]+static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
if settings.DEBUG:
    urlpatterns+=static(settings.MEDIA_URL,document_root=settings.MEDIA_ROOT)
