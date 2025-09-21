from django.contrib import admin
from django.urls import path
from cafeteria_app import views
from django.conf import settings
from django.conf.urls.static import static

urlpatterns = [
    path('', views.home, name='home'),              
    path('menu/', views.menu_list, name='menu'),    
    path('order/', views.place_order, name='place_order'),  
    path('order/confirm/', views.confirm_order, name='confirm_order'),  
    path('thanks/', views.thanks, name='thanks'),
    path('register/', views.register, name='register'), 
    path('admin/', admin.site.urls),
    path('order/add/<int:item_id>/', views.add_to_order, name='add_to_order'),
    
    path('check_your_order/', views.check_your_order, name='check_your_order'),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)