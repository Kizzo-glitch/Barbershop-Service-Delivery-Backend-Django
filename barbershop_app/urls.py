from django.urls import path, include
from . import views, apis
from django.contrib.auth import views as auth_views
from django.conf.urls.static import static
from django.conf import settings
from rest_framework import routers

# router = routers.DefaultRouter()
# router.register(r'heroes', views.HeroViewSet)

urlpatterns = [

        path('sign_up/', views.branch_sign_up, name="register"),
        path('sign_in/', auth_views.LoginView.as_view(template_name='branch/sign_in.html'), name="login"),
        path('sign_out/', auth_views.LogoutView.as_view(next_page='login'), name="logout"),
        path('', views.branch_home, name="branch_home"),

        path('account/', views.branch_account, name="account"),

        path('service/', views.branch_service, name="service"),
        path('service/add/', views.add_service, name="add-service"),
        path('service/<int:pk>/edit/', views.ServiceUpdateView.as_view(template_name='branch/edit_service.html'), name="edit-service"),
        path('service/<int:pk>/delete/', views.delete_service, name="delete-service"),

        path('booking/', views.branch_booking, name="booking"),
        path('report/', views.branch_report, name="report"),

        
        # Sign In/ Sign Up API
        path('api/social/', include('rest_framework_social_oauth2.urls')),

        # APIs
        path('api/booking/notification/<last_request_time>)/', apis.branch_booking_notification),

        # APIs for customers
        path('api/customer/branches/', apis.customer_get_branches),
        path('api/customer/services/<branch_id>/', apis.customer_get_services),
        path('api/customer/bookings/add/', apis.customer_add_booking),
        path('api/customer/bookings/latest', apis.customer_get_latest_booking),
        path('api/customer/barber/location', apis.customer_barber_location),

        # APIs for DRIVERS
        path('api/barber/booking/ready/', apis.barber_get_ready_booking),
        path('api/barber/booking/pick/', apis.barber_pick_booking),
        path('api/barber/booking/latest/', apis.barber_get_latest_booking),
        path('api/barber/booking/complete/', apis.barber_complete_booking),
        path('api/barber/revenue/', apis.barber_get_revenue),
        path('api/barber/location/update', apis.barber_update_location),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)

#urlpatterns += router