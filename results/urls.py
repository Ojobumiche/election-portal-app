from django.urls import path
from . import views



urlpatterns = [
    path('', views.polling_unit_result, name='home'),
    path('polling-unit-result/', views.polling_unit_result, name='polling_unit_result'),
    path('lga-results/', views.lga_summed_result, name='lga_result'),
    path('add-result/', views.add_polling_unit_result, name='add_result'),
]



