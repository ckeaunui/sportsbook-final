from django.urls import path
from . import views


urlpatterns = [
    path('', views.dashboard, name="dashboard"),
    path('login/', views.loginPage, name="login"),
    path('logout/', views.logoutUser, name="logout"),
    path('user/', views.userPage, name="user_page"),
    path('sports/<str:sport_group>/', views.sports, name="sports"),
    path('load_table/<str:sport_group>/<str:league_key>/<str:bet_type>/', views.load_table, name="load_table"),
    path('dashboard/', views.dashboard, name="dashboard"),
    path('register/', views.registerPage, name="register"),
    path('roulette/', views.roulette, name="roulette"),
    path('casino/', views.casino, name="casino"),
    path('blackjack/', views.blackjack, name="blackjack"),
    path(r'^delete_user/(?P<username>\d+)', views.delete_user, name="delete_user"),
    path("edit_user/<str:pk>/", views.edit_user, name="edit_user"),
    path("edit_order/<str:pk>/", views.edit_order, name="edit_order"),
    path("remove_from_cart/", views.remove_from_cart, name="remove_from_cart"),
    path("order_placed/<str:pk>/", views.order_placed, name="order_placed"),
    path("add_to_cart/", views.add_to_cart, name="add_to_cart"),
    path("edit_wager/", views.edit_wager, name="edit_wager"),
    path("checkout/", views.checkout, name="checkout"),
    path("place_order/", views.place_order, name="place_order"),
    path("get_prop_data/", views.get_prop_data, name="get_prop_data"),
    path("place_wager/", views.place_wager, name="place_wager"),
    path("add_to_balance/", views.add_to_balance, name="add_to_balance"),

    
]

