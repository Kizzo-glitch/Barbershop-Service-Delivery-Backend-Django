from rest_framework import serializers

from .models import Branches, Service, Customer, Barber, Booking, BookingDetail


class BranchSerializer(serializers.ModelSerializer):
    logo = serializers.SerializerMethodField()

    def get_logo(self, branch):
        request = self.context.get('request')
        logo_url = branch.logo.url
        return request.build_absolute_uri(logo_url)

    class Meta:
        model = Branches
        fields = ("id", "name", "phone", "address", "logo")


class ServiceSerializer(serializers.ModelSerializer):
    image = serializers.SerializerMethodField()

    def get_image(self, service):
        request = self.context.get('request')
        image_url = service.image.url
        return request.build_absolute_uri(image_url)

    class Meta:
        model = Service
        fields = ("id", "name", "short_description", "image", "price")


# BOOKING SERIALIZER
class BookingCustomerSerializer(serializers.ModelSerializer):
    name = serializers.ReadOnlyField(source="user.get_full_name")

    class Meta:
        model = Customer
        fields = ("id", "name", "avatar", "phone", "address")


class BookingBarberSerializer(serializers.ModelSerializer):
    name = serializers.ReadOnlyField(source="user.get_full_name")

    class Meta:
        model = Customer
        fields = ("id", "name", "avatar", "phone", "address")


class BookingBranchSerializer(serializers.ModelSerializer):
    class Meta:
        model = Branches
        fields = ("id", "name", "phone", "address")


class BookingServiceSerializer(serializers.ModelSerializer):
    class Meta:
        model = Service
        fields = ("id", "name", "price")


class BookingDetailsSerializer(serializers.ModelSerializer):
    service = BookingServiceSerializer()

    class Meta:
        model = BookingDetail
        fields = ("id", "service", "quantity", "sub_total")


class BookingSerializer(serializers.ModelSerializer):
    customer = BookingCustomerSerializer()
    barber = BookingBarberSerializer()
    branch = BookingBranchSerializer()
    booking_details = BookingDetailsSerializer(many=True)
    status = serializers.ReadOnlyField(source="get_status_display")

    class Meta:
        model = Booking
        fields = ("id", "customer", "branch", "barber", "booking_details", "total", "status", "address")
