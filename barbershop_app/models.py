from django.db import models
from django.contrib.auth.models import User
from django.utils import timezone


# Create your models here.
class Branches(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='branch')
    name = models.CharField(max_length=500)
    phone = models.CharField(max_length=500)
    address = models.CharField(max_length=500)
    logo = models.ImageField(upload_to='branch_logo/', blank=False)

    def __str__(self):
        return self.name


class Customer(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='customer')
    avatar = models.CharField(max_length=500)
    phone = models.CharField(max_length=500, blank=True)
    address = models.CharField(max_length=500, blank=True)

    def __str__(self):
        return self.user.get_full_name()


class Barber(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='barber')
    avatar = models.CharField(max_length=500)
    phone = models.CharField(max_length=500, blank=True)
    address = models.CharField(max_length=500, blank=True)
    location = models.CharField(max_length=500, blank=True)

    def __str__(self):
        return self.user.get_full_name()


class Service(models.Model):
    branch = models.ForeignKey(Branches, on_delete=models.CASCADE)
    name = models.CharField(max_length=500)
    short_description = models.CharField(max_length=500)
    image = models.ImageField(upload_to='service_images/', blank=False)
    price = models.IntegerField(default=0)

    def __str__(self):
        return self.name

    def save(self):
        super().save()

    # def get_absolute_url(self):
    #     return reverse('services', kwargs={'pk': self.pk})


class Booking(models.Model):
    WAITING = 1
    READY = 2
    COMING = 3
    DELIVERED = 4

    STATUS_CHOICES = (
        (WAITING, "Waiting for barber"),
        (READY, "Ready to move"),
        (COMING, "On the way"),
        (DELIVERED, "Service done"),
    )

    customer = models.ForeignKey(Customer, on_delete=models.CASCADE)
    branch = models.ForeignKey(Branches, on_delete=models.CASCADE)
    barber = models.ForeignKey(Barber, blank=True, null=True, on_delete=models.CASCADE)
    address = models.CharField(max_length=500)
    total = models.IntegerField()
    status = models.IntegerField(choices=STATUS_CHOICES)
    created_at = models.DateTimeField(default=timezone.now)
    picked_at = models.DateTimeField(blank=True, null=True)

    def __str__(self):
        return str(self.id)


class BookingDetail (models.Model):
    order = models.ForeignKey(Booking, on_delete=models.CASCADE, related_name='booking_details')
    service = models.ForeignKey(Service, on_delete=models.CASCADE)
    quantity = models.IntegerField()
    sub_total = models.IntegerField()

    def __str__(self):
        return str(self.id)