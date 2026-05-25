from django.urls import path
from django.views.generic.base import RedirectView
from django.contrib.staticfiles.storage import staticfiles_storage
from . import views

urlpatterns = [
    path("", views.home, name="home"),
    path("insurance/", views.insurance_view, name="insurance"),
    path("insurance/travel-insurance", views.travel_insurance_view, name="travel-insurance"),
    path("insurance/critical-illness-insurance", views.critical_insurance_view, name="critical-illness-insurance"),
    path("insurance/disability-insurance", views.disability_insurance_view, name="disability-insurance"),
    path("insurance/life-insurance", views.life_insurance_view, name="life-insurance"),
    path("insurance/corporate-insurance", views.corporate_insurance_view, name="corporate-insurance"),
    path("insurance/business-insurance", views.corporate_insurance_view, name="business-insurance"),
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
    path("resources/blog/", views.blog_view, name="blog"),
    path("resources/blog/<slug:slug>/", views.blog_article_view, name="blog-article"),
    path("resources/", views.resources_view, name="resources"),
    path("contact-us/", views.contact_view, name="contact"),
    path(
    "favicon.ico",
    RedirectView.as_view(
        url=staticfiles_storage.url("images/favicon.ico"),
        permanent=True
        )
    ),
]
