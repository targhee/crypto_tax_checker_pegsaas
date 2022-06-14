import os
from datetime import datetime
from django.contrib import messages
from django.http import HttpResponseRedirect
from django.shortcuts import render, redirect
from django.urls import reverse
from django.utils.translation import gettext_lazy as _
from django.db.models import Q
from .models import Historyfile
from .forms import CryptoHistoryUploadForm
from django.core.files.storage import default_storage
from apps.portfolio.helpers import load_and_parse_file

from apps.portfolio.models import Transaction

def drop_existing_files(user):
    # Drop any existing history files.
    exist_files = Historyfile.objects.filter(user=user)
    for e in exist_files:
        # e_file = os.path.join(settings.MEDIA_ROOT, str(e.upload_file))
        e_file = str(e.upload_file)
        print(f"Delete file located at {e_file}")
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
                try:
                    result = load_and_parse_file(request.user, nfile)
                except:
                    # delete the database entry.
                    drop_existing_files(request.user)
                    # Delete the physical file
                    if default_storage.exists(nfile):
                        default_storage.delete(nfile)
                messages.success(request, f"Success loading {os.path.basename(nfile)}")
                # Now delete the uploaded file since everything is saved.
                #drop_existing_files(request.user)

                #return redirect('portfolio:portfolio-home')

                dups = Transaction.objects.filter(duplicate=True)
                num_dups = dups.count()
                no_matches = Transaction.objects.filter(Q(match_num="0") & Q(trade_type="Send") | Q(trade_type='sell'))
                num_nomatches = no_matches.count()
                all_sales = Transaction.objects.filter(Q(trade_type='sell') | Q(trade_type='Send'))
                rewards = Transaction.objects.filter(Q(trade_type='misc_reward') | Q(trade_type='staking_reward') | Q(trade_type='airdrop'))
                summary = []
                # Create a list of all the years from 2015 until now
                for year in range(2015, int(datetime.now().year)):
                    str_year = str(year)
                    # Get all the sales from this year
                    year_sales = [x.in_qty for x in all_sales if (x.timestamp.strftime("%Y") == str_year)]
                    # Grab all the duplicate sales from that year
                    year_duplicate_sales = [x.in_qty for x in dups if (x.timestamp.strftime("%Y") == str_year) and \
                                            (x.trade_type == 'sell' or x.trade_type == 'Send')]
                    # Grab all the unmatches sales from that year
                    year_unmatched_sales = [x.in_qty for x in no_matches if (x.timestamp.strftime("%Y") == str_year)]
                    # Grab all the rewards from that year
                    year_rewards = [x.out_qty for x in rewards if (x.timestamp.strftime("%Y") == str_year)]
                    # Sums
                    sum_total_sales = sum(list(year_sales))
                    sum_duplicate_sales = sum(list(year_duplicate_sales))
                    sum_unmatched_sales = sum(list(year_unmatched_sales))
                    sum_rewards = sum(list(year_rewards))
                    #sum_sales = sum_total_sales + sum_duplicate_sales + sum_unmatched_sales
                    summary.append({
                        'year' : year,
                        'total_sales' : sum_total_sales,
                        'duplicate_sales' : sum_duplicate_sales,
                        'unmatched_sales' : sum_unmatched_sales,
                        'rewards': sum_rewards,
                    })
                #print(f"Summary = {summary}")
                return render(request, 'web/app_home.html', context={
                    'active_tab': 'dashboard',
                    'page_title': _('Dashboard'),
                    'form': form,
                    'summary': summary,
                    'duplicate_object_list': dups,
                    'num_dups': num_dups,
                    'nomatch_object_list': no_matches,
                    'num_nomatches': num_nomatches,
                    'subscription': subscription_holder.active_stripe_subscription})
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

