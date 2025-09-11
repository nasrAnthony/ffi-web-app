from django.urls import path
from . import views

urlpatterns = [
    path("", views.home, name="home"),
    path("insurance/", views.insurance_view, name="insurance"),
    path("insurance/travel-insurance", views.travel_insurance_view, name="travel-insurance"),
    path("insurance/critical-illness-insurance", views.critical_insurance_view, name="critical-illness-insurance"),
    path("insurance/disability-insurance", views.disability_insurance_view, name="disability-insurance"),
    path("insurance/life-insurance", views.life_insurance_view, name="life-insurance"),
    path("insurance/life-insurance/whole-life-insurance", views.whole_life_insurance_view, name="whole-life-insurance"),
    path("insurance/life-insurance/term-life-insurance", views.term_life_insurance_view, name="term-life-insurance"),
    path("insurance/life-insurance/universal-life-insurance", views.universal_life_insurance_view, name="universal-life-insurance"),
    path("insurance/group-health-insurance", views.group_health_insurance_view, name="group-health-insurance"),
    path("insurance/partnership-insurance", views.partnership_insurance_view, name="partnership-insurance"),
    path("insurance/key-person-insurance", views.key_person_insurance_view, name="key-person-insurance"),
    path("investments/", views.investments_view, name="investments"),
    path("investments/corporate-investments", views.corporate_investments_view, name="corporate-investments"),
    path("investments/non-registered-investments", views.non_registered_investments_view, name="non-registered-investments"),
    path("investments/registered-investments", views.registered_investments_view, name="registered-investments"),
    path("investments/rrsp-investments", views.rrsp_investments_view, name="rrsp-investments"),
    path("about-us/", views.about_view, name="about"),
    path("resources/", views.resources_view, name="resources"),
    path("contact-us/", views.contact_view, name="contact"),
]