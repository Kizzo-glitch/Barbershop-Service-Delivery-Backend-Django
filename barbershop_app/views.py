from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required

from django.contrib.auth.models import User
from django.contrib.auth import authenticate, login

from barbershop_app.models import Service, Booking, Barber
from barbershop_app.forms import ManagerForm, BranchForm, ManagerFormEdit, ServiceForm

from django.db.models import Sum, Count, Case, When

from django.views.generic import UpdateView, DeleteView
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin


def home(request):
    return redirect(branch_home)


@login_required(login_url='/sign_in/')
def branch_home(request):
    return redirect(branch_booking)


@login_required(login_url='/sign_in/')
def branch_account(request):
    manager_form = ManagerFormEdit(instance=request.user)
    branch_form = BranchForm(instance=request.user)

    if request.method == "POST":
        manager_form = ManagerFormEdit(request.POST, instance=request.user)
        branch_form = BranchForm(request.POST, request.FILES, instance=request.user.branch)

        if manager_form.is_valid() and branch_form.is_valid():
            manager_form.save()
            branch_form.save()

    return render(request, 'branch/account.html/', {
        'manager_form': manager_form,
        'branch_form': branch_form
    })


@login_required(login_url='/sign_in/')
def branch_service(request):
    services = Service.objects.filter(branch=request.user.branch).order_by('-id')
    return render(request, 'branch/service.html/', {'services': services})


@login_required(login_url='/sign_in/')
def add_service(request):
    form = ServiceForm()

    if request.method == "POST":
        form = ServiceForm(request.POST, request.FILES)

        if form.is_valid():
            service = form.save(commit=False)
            service.branch = request.user.branch
            service.save()
            return redirect(branch_service)

    return render(request, 'branch/add_service.html/', {
        "form": form
    })


class ServiceUpdateView(UpdateView):
    model = Service
    fields = ['name', 'short_description', 'image', 'price']
    success_url = '/'

    def form_valid(self, form):
        form.instance.branch = self.request.user.branch
        return super().form_valid(form)

    # def test_func(self):
    #     service = self.get_object()
    #     if self.request.user.branch == service.branch:
    #         return True
    #     return False


def delete_service(request, pk):
    Service.objects.filter(id=pk).delete()
    service = Service.objects.all()
    context = {'service': service}
    return render(request, 'branch/service.html', context)
# class ServiceDeleteView(DeleteView):
#     model = Service
#     success_url = 'service'

    # def test_func(self):
    #     post = self.get_object()
    #     if self.request.user == post.branch:
    #         return True
    #     return False





#
# @login_required(login_url='/sign_in/')
# def edit_service(request, slug):
#
#     post = get_object_or_404(Service, slug=slug)
#     if request.method == "POST":
#         form = ServiceForm(request.POST, request.FILES, instance=post)
#         if form.is_valid():
#             service = form.save()
#             service.branch = request.user.branch
#             service.save()
#             return redirect(branch_service)
#     else:
#         form = ServiceForm(instance=post)
#
#     return render(request, 'branch/edit_service.html/', {
#         "form": form
#     })


@login_required(login_url='/sign_in/')
def branch_booking(request):
    if request.method == "POST":
        booking = Booking.objects.get(id=request.POST["id"], branch=request.user.branch)

        if booking.status == Booking.WAITING:
            booking.status = Booking.READY
            booking.save()

    bookings = Booking.objects.filter(branch=request.user.branch).order_by("-id")
    return render(request, 'branch/booking.html/', {'bookings': bookings})


@login_required(login_url='/sign_in/')
def branch_report(request):
    # Calculate revenue and number of bookings by current week
    from datetime import datetime, timedelta

    revenue = []
    bookings = []

    # Calculate weekdays
    today = datetime.now()
    current_weekdays = [today + timedelta(days=i) for i in range(0 - today.weekday(), 7 - today.weekday())]

    for day in current_weekdays:
        delivered_bookings = Booking.objects.filter(
            branch=request.user.branch,
            status=Booking.DELIVERED,
            created_at__year=day.year,
            created_at__month=day.month,
            created_at__day=day.day
        )
        revenue.append(sum(booking.total for booking in delivered_bookings))
        bookings.append(delivered_bookings.count())

    # Top 3 Services
    top3_services = Service.objects.filter(branch=request.user.branch)\
                     .annotate(total_booking=Sum('bookingdetail__quantity'))\
                     .order_by("-total_booking")[:3]

    service = {
        "labels": [service.name for service in top3_services],
        "data": [service.total_booking or 0 for service in top3_services]
    }

    # Top 3 Barbers
    top3_barbers = Barber.objects.annotate(
        total_booking=Count(
            Case(
                When(booking__branch=request.user.branch, then=1)
            )
        )
    ).order_by("-total_booking")[:3]

    barber = {
        "labels": [barber.user.get_full_name() for barber in top3_barbers],
        "data": [barber.total_booking for barber in top3_barbers]
    }

    return render(request, 'branch/report.html', {
        "revenue": revenue,
        "booking": bookings,
        "service": service,
        "barber": barber
    })


def branch_sign_up(request):
    manager_form = ManagerForm()
    branch_form = BranchForm()

    if request.method == "POST":
        manager_form = ManagerForm(request.POST)
        branch_form = BranchForm(request.POST, request.FILES)

        if manager_form.is_valid() and branch_form.is_valid():
            new_user = User.objects.create_user(**manager_form.cleaned_data)
            new_branch = branch_form.save(commit=False)
            new_branch.user = new_user
            new_branch.save()

            login(request, authenticate(
                username=manager_form.cleaned_data["username"],
                password=manager_form.cleaned_data["password"]
            ))

            return redirect(branch_home)

    return render(request, 'branch/sign_up.html/', {
        "manager_form": manager_form,
        "branch_form": branch_form
    })

