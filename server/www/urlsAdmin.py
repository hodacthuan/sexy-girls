from django.urls import path
from . import viewsAdmin
from django.conf import settings
from django.conf.urls.static import static


urlpatterns = [
    path('login', viewsAdmin.login),
    path('password', viewsAdmin.password),
    path('register', viewsAdmin.register),
    path('dashboard', viewsAdmin.dashboard),
    path('database/album', viewsAdmin.databaseAlbum)


] + static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
