from django.contrib import admin
from django.urls import path, include

urlpatterns = [
    path('admin/', admin.site.urls),
    path('performers/', include('performers.urls')),
    path('car-washes/', include('car_washes.urls')),
]
