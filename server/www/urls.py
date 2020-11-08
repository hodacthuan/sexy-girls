from django.urls import path
from . import views
from django.conf import settings
from django.conf.urls.static import static


urlpatterns = [
    path('', views.home),
    path('models', views.models),
    path('gallery', views.gallery),
    path('trending', views.gallery),
    path('about', views.about),
    path('hello', views.hello),
    path('image/<str:imagePath>/<str:imageFileName>', views.images),
    path('album/<str:albumTitle>', views.albums), ] + static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
