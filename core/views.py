from django.shortcuts import render, get_object_or_404, redirect
from django.http import HttpResponse
from django.views.decorators.csrf import csrf_exempt
from typing import Type
from django.conf import settings
from django.db import transaction
from django.db.models import Model
from django.core.exceptions import ValidationError
from django.utils.decorators import method_decorator
from django.contrib import messages
from django.core.paginator import Paginator
from django.db.models import Q
from django.urls import reverse
import stripe
import json

from .models import Course, EnrolledCustomer, Payment, CourseRegistration, FeedBack
from .forms import CourseRegistrationForm
from .serializers import serialize_tracks, serialize_upcoming


# Create your views here.
def index_view(request):
    return render(request, 'index.html')


def contact_view(request):
    if request.method == 'POST':
        name = request.POST.get('full_name')
        email = request.POST.get('email')
        message = f"Organisation: {request.POST.get('organisation')}\nRole/Title: {request.POST.get('role')}\nInterest: {request.POST.get('interest')}"

        FeedBack(name=name, email=email, message=message).save()
        messages.success(request, 'Your message has been sent successfully!')
        return redirect('contact')

    return render(request, 'contact.html')


def akademie_view(request):
    context = {
        'tracks_json': json.dumps(serialize_tracks(), ensure_ascii=False),
        'upcoming_json': json.dumps(serialize_upcoming(), ensure_ascii=False),
    }
    return render(request, 'akademie.html', context)


def imprint_view(request):
    return render(request, 'imprint.html')


def privacy_view(request):
    return render(request, 'privacy.html')


def faculty_view(request):
    return render(request, 'faculty.html')


def geotech_view(request):
    return render(request, 'geotech.html')


def insights_view(request):
    return render(request, 'intelligence.html')


def payment_page(request, id):
    """This view send and displays the enrollment page

    """
    course = get_object_or_404(Course, id=id)
    return render(request, 'ihrdc_layout/course_payment.html', {'stripe_key': settings.STRIPE_PUBLIC_KEY, 'course': course})


def createstripe_checkout_session(request, id):
    """Takes the details from the enrollment page and handles payment.
    Create a checkout session and redirect the user to Stripe's checkout page
    """

    current_domain = f"{request.scheme}://{request.get_host()}"
    print(current_domain)
    course = Course.objects.get(id=id)

    if request.method == 'POST':
        customer = request.POST.get('customer', '')
        email = request.POST.get('email', '')
        phone = request.POST.get('phone', '')
        city = request.POST.get('city', '')
        country = request.POST.get('country', '')
        postcode = request.POST.get('postcode', '')
        quantity = request.POST.get('quantity', 1)
        currency = request.POST.get('currency', 'USD')

    image_url = course.image.url if course.image else '/static/layout/images/default_course_img.jfif'

    # creating enrolled customer
    enrolled = EnrolledCustomer.objects.create(
        customer=customer,
        email=email,
        phone_number=phone,
        city=city,
        country=country,
        postcode=postcode,
        course=course,
    )
    enrolled.save()

    # creating payment history
    transaction = Payment.objects.create(
        customer=enrolled,
        currency=currency,
        amount=int(course.price) * int(quantity),
        quantity=quantity,
    )
    transaction.save()

    # Create a Stripe checkout session
    checkout_session = stripe.checkout.Session.create(
        payment_method_types=["card", "us_bank_account"],  # "paypal",
        line_items=[
            {
                "price_data": {
                    "currency": str(currency).lower(),
                    "unit_amount": int(course.price) * 100,
                    "product_data": {
                        "name": course.title,
                        "description": course.description,
                        "images": [
                            f"{current_domain}{image_url}"
                        ],
                    },
                },
                "quantity": int(quantity),
            }
        ],
        metadata={"product_id": course.id, 'payment_id': transaction.id},
        mode="payment",
        success_url=request.build_absolute_uri('/success/'),
        cancel_url=request.build_absolute_uri('/cancel/'),
    )
    return redirect(checkout_session.url)


def success(request):
    return render(request, "ihrdc_layout/success.html")


def cancel(request):
    return render(request, "ihrdc_layout/cancel.html")


@method_decorator(csrf_exempt, name="dispatch")
def stripe_webhook(request, format=None):
    """
    Stripe webhook view to handle checkout session completed event.
    """
    payload = request.body
    endpoint_secret = settings.STRIPE_SECRET_KEY
    sig_header = request.META["HTTP_STRIPE_SIGNATURE"]
    event = None

    try:
        event = stripe.Webhook.construct_event(payload, sig_header, endpoint_secret)
    except ValueError as e:
        # Invalid payload
        return HttpResponse(status=400)
    except stripe.error.SignatureVerificationError as e:
        # Invalid signature
        return HttpResponse(status=400)

    if event["type"] == "checkout.session.completed":
        print("Payment successful")

        # Add this
        session = event["data"]["object"]
        customer_email = session["customer_details"]["email"]
        product_id = session["metadata"]["product_id"]
        product = get_object_or_404(Course, id=product_id)
        payment_id = session["metadata"]["payment_id"]
        payment = get_object_or_404(Payment, id=payment_id)
        payment.payment_status = "completed"
        payment.save()

        # send_mail(
        #     subject="Here is your product",
        #     message=f"Thanks for your purchase. The URL is: {product.url}",
        #     recipient_list=[customer_email],
        #     from_email="your@email.com",
        # )

    return HttpResponse(status=200)


def register_course(request):
    courses = Course.objects.select_related('category', 'cluster').all()
    selected_course = None
    requested_course_id = (
        request.POST.get('course_id')
        if request.method == 'POST'
        else request.GET.get('course_id')
    )

    if requested_course_id:
        selected_course = Course.objects.filter(id=requested_course_id).select_related(
            'category',
            'cluster',
        ).first()

    if request.method == 'POST':
        form = CourseRegistrationForm(request.POST)

        if not requested_course_id:
            form.add_error(None, 'Choose a course before submitting your registration.')
        elif not selected_course:
            form.add_error(None, 'Choose a valid course before submitting your registration.')

        if form.is_valid() and selected_course:
            registration = form.save(commit=False)
            registration.course = selected_course
            registration.save()

            messages.success(
                request,
                'Registration received. Our admissions team will contact you within one business day.',
            )
            return redirect(f"{reverse('register_course')}?course_id={selected_course.id}")

        messages.error(request, 'Please correct the highlighted fields.')
    else:
        form = CourseRegistrationForm()

    return render(
        request,
        'register.html',
        {
            'form': form,
            'courses': courses,
            'selected_course': selected_course,
        },
    )
