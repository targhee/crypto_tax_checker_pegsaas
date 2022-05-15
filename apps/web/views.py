import os
from django.contrib import messages
from django.http import HttpResponseRedirect
from django.shortcuts import render, redirect
from django.urls import reverse
from django.utils.translation import gettext_lazy as _
from .models import Historyfile
from .forms import CryptoHistoryUploadForm
from django.core.files.storage import default_storage
from apps.portfolio.helpers import load_and_parse_file

def drop_existing_files(user):
    # Drop any existing history files.
    exist_files = Historyfile.objects.filter(user=user)
    for e in exist_files:
        # e_file = os.path.join(settings.MEDIA_ROOT, str(e.upload_file))
        e_file = str(e.upload_file)
        print(f"File located at {e_file}")
        # Delete the physical file
        if default_storage.exists(e_file):
            default_storage.delete(e_file)
        # delete the database entry.
        e.delete()
    return

def home(request):
    if request.user.is_authenticated:
        subscription_holder = request.user
        if request.method == 'POST':
            print(f"Request User: {request.user}")
            print(f"Request FILES: {request.FILES}")
            form = CryptoHistoryUploadForm(request.POST, request.FILES)
            if form.is_valid():
                # Drop any existing history files.
                drop_existing_files(request.user)
                crypto_history = form.save(commit=False)
                crypto_history.user = request.user
                crypto_history.save()
                nfile = str(crypto_history.upload_file)
                print(f"Crypto History Filename: {nfile}")
                # Now let's read and parse the file.
                result = load_and_parse_file(request.user, nfile)
                messages.success(request, f"Success loading {os.path.basename(nfile)}")
                # Now delete the uploaded file since everything is saved.
                #drop_existing_files(request.user)

                return redirect('portfolio:portfolio-home')
                # return render(request, 'web/app_home.html', context={
                #     'active_tab': 'dashboard',
                #     'page_title': _('Dashboard'),
                #     'form': form,
                #     'subscription': subscription_holder.active_stripe_subscription})
        else:
            print("Initial read of the form")
            form = CryptoHistoryUploadForm()
            return render(request, 'web/app_home.html', context={
                'active_tab': 'dashboard',
                'page_title': _('Dashboard'),
                'form': form,
                'subscription': subscription_holder.active_stripe_subscription})
    else:
        return render(request, 'web/landing_page.html')


def simulate_error(request):
    raise Exception('This is a simulated error.')

