from django.urls import path
from . import views
from accounts import views as account_views

app_name = 'hotels'

urlpatterns = [
    # Public / customer pages
    path('', views.hotel_list, name='hotel_list'),
    path('<int:hotel_id>/', views.hotel_detail, name='hotel_detail'),

    path("book-table/<int:restaurant_id>/", views.book_table, name="book_table"),


    path('booking-summary/<int:booking_id>/', views.booking_summary, name='booking_summary'),

    path('<int:hotel_id>/map/', views.map_page, name='map_page'),
    path('<int:hotel_id>/reviews/', views.reviews_page, name='reviews_page'),
    path('my_reservations/', views.my_reservations, name='my_reservations'),

    # Owner authentication
    path('owner/register/', views.owner_register, name='owner_register'),
    path('owner/login/', views.owner_login, name='owner_login'),
    path('owner/logout/', views.owner_logout, name='owner_logout'),

    # Fixed edit_menu_item path
    path('owner/edit_menu/<int:item_id>/', views.edit_menu_item, name='edit_menu_item'),
    path('owner/delete_menu/<int:item_id>/', views.delete_menu_item, name='delete_menu_item'),

    # Owner pages
    path('owner/dashboard/', views.owner_dashboard, name='owner_dashboard'),
    path('owner/add_menu/<int:restaurant_id>/', views.add_menu_item, name='add_menu_item'),

    # New URL for updating order status
    path('owner/update_order/<int:order_id>/', views.update_order_status, name='update_order_status'),
    path("cart/", views.cart_page, name="cart_page"),
    path("place-order/", views.place_order, name="place_order"),
    path("cart-add/<int:item_id>/", views.cart_add, name="cart_add"),
    path("clear-cart/", views.clear_cart, name="clear_cart"),
    path('my_reservations_ajax/', views.my_reservations_ajax, name='my_reservations_ajax'),
    path("receipt/<int:order_id>/", views.order_receipt, name="order_receipt"),
    path("admin/dashboard/", views.admin_dashboard, name="admin_dashboard"),
    path("admin/approve/<int:restaurant_id>/", views.approve_restaurant, name="approve_restaurant"),
    path("admin/reject/<int:restaurant_id>/", views.reject_restaurant, name="reject_restaurant"),
    path("admin/delete/<int:restaurant_id>/", views.delete_restaurant, name="delete_restaurant"),
    path("owner/bookings/", views.owner_bookings, name="owner_bookings"),
    path("owner/booking/<int:booking_id>/<str:action>/", views.update_booking_status, name="update_booking_status"),
    path("owner/booking/<int:booking_id>/accept/", views.accept_booking, name="accept_booking"),
    path("owner/booking/<int:booking_id>/reject/", views.reject_booking, name="reject_booking"),



]
