from django.contrib import admin
from django.urls import path, include

urlpatterns = [
    path('admin/', admin.site.urls),
    path('staff/', include('staff.urls')),
    path('car-washes/', include('car_washes.urls')),
    path('mailing/', include('mailing.urls')),
    path('economics/', include('economics.urls')),
]
