from django.urls import path
from . import views

urlpatterns = [
    path('register/',views.RegisterUserView.as_view()),
    path('login/', views.LoginView.as_view()),
    path('logout/', views.LogoutView.as_view()),
    path('foods/', views.FoodListView.as_view()),
    path('foods/<id>/', views.FoodDetailView.as_view()),
    path('orders/', views.OrderListView.as_view()),
    path('orders/create/', views.OrderCreateView.as_view()),
    path('orders/<id>/', views.OrderDetailView.as_view()),
    path('orders/<id>/update/', views.OrderUpdateView.as_view()),
    path('orders/<id>/delete/', views.OrderDeleteView.as_view()),
    path('news/', views.NewItems.as_view()),
    path('myorders/', views.UserOrders.as_view()),
]