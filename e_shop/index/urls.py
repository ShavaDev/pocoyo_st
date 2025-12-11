from django.urls import path
from . import views

urlpatterns = [
    path('', views.home_page),
    path('category/<int:pk>/', views.category_page),
    path('product/<int:pk>/', views.product_page),
    path('add-to-cart/<int:pk>', views.add_to_cart),
    path('search', views.search),
    path('register', views.Register.as_view()),
    path('logout', views.logout_view),
    path('cart/', views.cart_page),
    path('del-from-cart/<int:pk>', views.del_from_cart)
]
