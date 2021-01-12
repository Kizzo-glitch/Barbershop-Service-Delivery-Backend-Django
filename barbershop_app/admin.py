from django.contrib import admin

# Register your models here.
from barbershop_app.models import Branches, Customer, Barber, Service, Booking, BookingDetail

admin.site.register(Branches)
admin.site.register(Customer)
admin.site.register(Barber)
admin.site.register(Service)
admin.site.register(Booking)
admin.site.register(BookingDetail)