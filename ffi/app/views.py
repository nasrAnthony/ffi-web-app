from django.shortcuts import render
from django.utils import timezone
from django.conf import settings
from django.shortcuts import render, redirect
from .forms import ContactForm
from django.contrib import messages
from .gmail_api import send_contact_emails
# Create your views here.

#base page...
def home(request):
    if request.method == "POST":
        form = ContactForm(request.POST)
        if form.is_valid():
            data = form.cleaned_data
            ctx = {
                "name": data["name"],
                "email": data["email"],
                "phone": data.get("phone"),
                "preferred_contact": data.get("preferred_contact"),
                "topic": data.get("topic"),
                "subject": f"{data.get('topic', 'General Question')} — {data['name']}",
                "message": data["message"],
                "firm_name": "Family First Insurance",
                "submitted_at": timezone.now(),
            }
            try:
                send_contact_emails(
                    ctx=ctx,
                    customer_email=ctx["email"],
                    internal_email=INTERNAL_CONTACT,
                    from_identity=FROM_IDENTITY,
                )

                messages.success(
                    request,
                    "Success — we have received your message and will be with you shortly."
                )

            except Exception as e:
                print(e)
                messages.error(
                    request,
                    "Sorry, we failed to send your request. Please try again."
                )
        else:
            messages.error(request, "Please correct the errors below and resubmit.")
    else:
        form = ContactForm()

    return render(request, "app/home_page.html", {"form": form})

def insurance_view(request):
    return render(request, "app/insurance/insurance.html")

def life_insurance_view(request):
    return render(request, "app/insurance/life_insurance_page.html")

def whole_life_insurance_view(request):
    return render(request, "app/insurance/whole_life_insurance_page.html")

def term_life_insurance_view(request):
    return render(request, "app/insurance/term_life_insurance_page.html")

def universal_life_insurance_view(request):
    return render(request, "app/insurance/universal_life_insurance_page.html")

def critical_insurance_view(request):
    return render(request, "app/insurance/critical_illness_insurance_page.html")

def disability_insurance_view(request):
    return render(request, "app/insurance/disability_insurance_page.html")

def travel_insurance_view(request):
    return render(request, "app/insurance/travel_insurance_page.html")

def group_health_insurance_view(request):
    return render(request, "app/corporate-insurance/group_health_insurance_page.html")

def partnership_insurance_view(request):
    return render(request, "app/corporate-insurance/partnership_insurance_page.html")

def key_person_insurance_view(request):
    return render(request, "app/corporate-insurance/key_person_insurance_page.html")

def about_view(request):
    return render(request, "app/about_page.html")

def resources_view(request):
    return render(request, "app/resources_page.html")


INTERNAL_CONTACT = "epic2battle3@gmail.com"
FROM_IDENTITY    = settings.DEFAULT_FROM_EMAIL

def contact_view(request):
    if request.method == "POST":
        form = ContactForm(request.POST)
        if form.is_valid():
            data = form.cleaned_data

            # Build context for templates
            ctx = {
                "name": data["name"],
                "email": data["email"],
                "phone": data.get("phone"),
                "preferred_contact": data.get("preferred_contact"),
                "topic": data.get("topic"),
                "subject": f"{data.get('topic', 'General Question')} — {data['name']}",
                "message": data["message"],
                "firm_name": "Family First Insurance",
                "submitted_at": timezone.now(),
            }

            # Send both emails (ack to customer + forward to internal)
            try:
                send_contact_emails(
                    ctx=ctx,
                    customer_email=ctx["email"],
                    internal_email=INTERNAL_CONTACT,
                    from_identity=FROM_IDENTITY,
                )
                messages.success(
                    request,
                    "Success — we have received your message and will be with you shortly."
                )
            except Exception as e:
                messages.error(
                    request,
                    "Sorry, we failed to send your request. Please try again."
                )
        else:
            messages.error(request, "Please correct the errors below and resubmit.")

    else:
        form = ContactForm()

    return render(request, "app/contact_page.html", {"form": form})

def investments_view(request):
    return render(request, "app/investment/investments_page.html")

def corporate_investments_view(request):
    return render(request, "app/investment/corp_investments_page.html")

def non_registered_investments_view(request):
    return render(request, "app/investment/non_registered_investments_page.html")

def registered_investments_view(request):
    return render(request, "app/investment/registered_investments_page.html")

def rrsp_investments_view(request):
    return render(request, "app/investment/rrsp_investments_page.html")

