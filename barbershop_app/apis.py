import json

from django.utils import timezone
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt

from oauth2_provider.models import AccessToken

from .models import Branches, Service, Booking, BookingDetail, Barber
from .serializers import BranchSerializer, ServiceSerializer, BookingSerializer

import stripe
from barbershop.settings import STRIPE_API_KEY

stripe.api_key = STRIPE_API_KEY


##########
# CUSTOMERS
##########
def customer_get_branches(request):
    branches = BranchSerializer(
        Branches.objects.all().order_by("-id"),
        many=True,
        context={"request": request}
    ).data

    return JsonResponse({"branches": branches})


def customer_get_services(request, branch_id):
    services = ServiceSerializer(
        Service.objects.filter(branch_id=branch_id).order_by("-id"),
        many=True,
        context={"request": request}
    ).data

    return JsonResponse({"services": services})


@csrf_exempt
def customer_add_booking(request):
    """
        params:
            access_token
            branch_id
            address
            booking_details (json format), example:
                [{"service_id": 1, "quantity": 2},{"service_id": 2, "quantity": 3}]
            stripe_token

        return:
            {"status": "success"}
    """

    if request.method == "POST":
        # Get token
        access_token = AccessToken.objects.get(token=request.POST.get("access_token"),
            expires__gt=timezone.now())

        # Get profile
        customer = access_token.user.customer

        # Get stripe token
        stripe_token = request.POST["stripe_token"]

        # Check whether customer has any booking that is not delivered
        if Booking.objects.filter(customer=customer).exclude(status=Booking.DELIVERED):
            return JsonResponse({"status": "failed", "error": "Your last booking must be completed."})

        # Check Address
        if not request.POST["address"]:
            return JsonResponse({"status": "failed", "error": "Address is required."})

        # Get Booking Details
        booking_details = json.loads(request.POST["booking_details"])

        booking_total = 0
        for service in booking_details:
            booking_total += Service.objects.get(id=service["service_id"]).price * service["quantity"]

        if len(booking_details) > 0:

            # Step 1: Create a charge for customer's card
            charge = stripe.Charge.create(
                amount = booking_total * 100,
                currency = "zar",
                source = stripe_token,
                description = "Barbershop Booking"
                )

            if charge.status != "failed":
                # Step 1 - Create booking
                booking = Booking.objects.create(
                    customer=customer,
                    branch_id=request.POST["branch_id"],
                    total=booking_total,
                    status=Booking.WAITING,
                    address=request.POST["address"]
                )

                # Step 2 - Create booking details
                for service in booking_details:
                    BookingDetail.objects.create(
                        booking=booking,
                        service_id=service["service_id"],
                        quantity=service["quantity"],
                        sub_total=Service.objects.get(id=service["service_id"]).price * service["quantity"]
                    )

                return JsonResponse({"status": "success"})

            else:
                return JsonResponse({"status": "failed", "error": "Failed to connect to Stripe"})



def customer_get_latest_booking(request):
    access_token = AccessToken.objects.get(token=request.GET.get("access_token"),
        expires__gt=timezone.now())

    customer = access_token.user.customer
    booking = BookingSerializer(Booking.objects.filter(customer=customer).last()).data

    return JsonResponse({"booking": booking})


def customer_barber_location(request):
    access_token = AccessToken.objects.get(token=request.GET.get("access_token"),
        expires__gt=timezone.now())

    customer = access_token.user.customer

    # Get driver's location related to this customer's current order.
    current_booking = Booking.objects.filter(customer=customer, status=Booking.DELIVERED).last()
    location = current_booking.barber.location

    return JsonResponse({"location": location})


##########
# BRANCH
#########
def branch_booking_notification(request, last_request_time):
    notification = Booking.objects.filter(branch=request.user.branch,
        created_at__gt=last_request_time).count()

    return JsonResponse({"notification": notification})


##########
# BARBERS
##########
def barber_get_ready_booking(request):
    bookings = BookingSerializer(
        Booking.objects.filter(status=Booking.READY, driver=None).order_by("-id"),
        many=True
    ).data

    return JsonResponse({"bookings": bookings})

@csrf_exempt
# POST
# params: access_token, booking_id
def barber_pick_booking(request):

    if request.method == "POST":
        # Get token
        access_token = AccessToken.objects.get(token=request.POST.get("access_token"),
            expires__gt=timezone.now())

        # Get barber
        barber = access_token.user.barber

        # Check if barber can only pick up one booking at the same time
        if Booking.objects.filter(barber=barber).exclude(status=Booking.DELIVERED):
            return JsonResponse({"status": "failed", "error": "You can only pick one booking at the same time."})

        try:
            booking = Booking.objects.get(
                id=request.POST["booking_id"],
                barber=None,
                status=Booking.READY
            )
            booking.barber = barber
            booking.status = Booking.ONTHEWAY
            booking.picked_at = timezone.now()
            booking.save()

            return JsonResponse({"status": "success"})

        except Booking.DoesNotExist:
            return JsonResponse({"status": "failed", "error": "This booking has been picked up by another."})

    return JsonResponse({})


# GET params: access_token
def barber_get_latest_booking(request):
    # Get token
    access_token = AccessToken.objects.get(token=request.GET.get("access_token"),
        expires__gt=timezone.now())

    barber = access_token.user.barber
    booking = BookingSerializer(
        Booking.objects.filter(barber=barber).order_by("picked_at").last()
    ).data

    return JsonResponse({"booking": booking})

# POST params: access_token, booking_id
@csrf_exempt
def barber_complete_booking(request):
    # Get token
    access_token = AccessToken.objects.get(token=request.POST.get("access_token"),
        expires__gt=timezone.now())

    barber = access_token.user.barber

    booking = Booking.objects.get(id=request.POST["booking_id"], barber=barber)
    booking.status = Booking.DELIVERED
    booking.save()

    return JsonResponse({"status": "success"})

# GET params: access_token
def barber_get_revenue(request):
    access_token = AccessToken.objects.get(token=request.GET.get("access_token"),
        expires__gt=timezone.now())

    barber = access_token.user.barber

    from datetime import timedelta

    revenue = {}
    today = timezone.now()
    current_weekdays = [today + timedelta(days=i) for i in range(0 - today.weekday(), 7 - today.weekday())]

    for day in current_weekdays:
        bookings = Booking.objects.filter(
            barber=barber,
            status=Booking.DELIVERED,
            created_at__year=day.year,
            created_at__month=day.month,
            created_at__day=day.day
        )

        revenue[day.strftime("%a")] = sum(booking.total for booking in bookings)

    return JsonResponse({"revenue": revenue})


# POST - params: access_token, "lat,lng"
@csrf_exempt
def barber_update_location(request):
    if request.method == "POST":
        access_token = AccessToken.objects.get(token=request.POST.get("access_token"),
            expires__gt=timezone.now())

        barber = access_token.user.barber

        # Set location string => database
        barber.location = request.POST["location"]
        barber.save()

        return JsonResponse({"status": "success"})