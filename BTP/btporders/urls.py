from django.urls import path
from btporders import views

urlpatterns = [
    path('savedata/', views.saveOrders),
    path('tabledata/', views.getDatas),
]