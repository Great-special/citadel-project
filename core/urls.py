from django.urls import path
from . import views

urlpatterns = [
    path('', views.index_view, name='index'),
    path('akademie/', views.akademie_view, name='akademie'),
    path('geotech/', views.geotech_view, name='geotech'),
    path('faculty/', views.faculty_view, name='faculty'),
    path('imprint/', views.imprint_view, name='imprint'), 
    path('contact/', views.contact_view, name='contact'),
    path('intelligence/', views.insights_view, name='insights'),
    path('privacy/', views.privacy_view, name='privacy'),
    
    path('register-course/', views.register_course, name='register_course'),
    path('payment-checkout/<int:id>/', views.payment_page, name='payment_page'),
    path('create-checkout-session/<int:id>/', views.createstripe_checkout_session, name='create_checkout_session'),
    
    path('cancel/', views.cancel, name='cancel'),
    path('success/', views.success, name='success'),
    path("webhooks/stripe/", views.stripe_webhook, name="stripe_webhook"),
    
]