from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.urls import reverse
import time, os
from crypto_tax_checker import settings
from django.core.files.storage import default_storage

import csv
import crypto.zen_transaction
import crypto.cryptotax_functions

from apps.portfolio.models import Transaction
from .models import Historyfile
from .forms import CryptoHistoryUploadForm

# Create your views here.
@login_required
def loader_home(request):
	return render(request, 'loader/loader_home.html')

def remove_user_records(user):
	Transaction.objects.filter(user=user).delete()
	return

@login_required
def loader_clear_table(request):
	print("Clearing the table")
	remove_user_records(request.user)
	return redirect('portfolio-home')

def loader_load_home(request, file_2_process):
	remove_user_records(request.user)
	tx_class_list = crypto.zen_transaction.process_zen_ledger(file_2_process)
	transaction_list = sorted(
		list(tx_class_list),
		key=lambda o: o.timestamp)

	# Run some audits on the incoming transactions
	# A simple check for duplicated transactions
	duplicate_list, duplicate_string = crypto.cryptotax_functions.find_duplicated_transactions(transaction_list)
	print("---------------------------------------------------------")
	print(duplicate_string)
	print("---------------------------------------------------------")
	print(f"Size of duplicates is {len(duplicate_list)}")
	for transaction in duplicate_list:
		print(f"Duplicate: {transaction}")

	transactions, matched_pairs, unmatched_tx, function_desc_string =\
		crypto.cryptotax_functions.find_paired_transactions4(transaction_list)

	# with open("loader/files/sorted_transaction_list.csv", 'w') as sorted_file:
	# 	for transaction in transaction_list:
	# 		# print(transaction)
	# 		print(transaction, file=sorted_file)
	# print("---------------------------------------------------------")
	for transaction in transaction_list:
		t = Transaction(user=request.user, timestamp=transaction.timestamp,
						trade_type=transaction.trade_type, in_asset=transaction.in_tx.asset,
						in_qty=transaction.in_tx.qty, out_asset=transaction.out_tx.asset,
						out_qty=transaction.out_tx.qty, fee_asset=transaction.fee.asset,
						fee_qty=transaction.fee.qty, tx_id=transaction.tx_id,
						exchange=transaction.exchange, part=transaction.part,
						reconciled=transaction.reconciled, match_num=transaction.match_num,
						duplicate=transaction.duplicate)
		t.save()
	messages.success(request, f"Success loading {os.path.basename(file_2_process)}")
	return redirect('portfolio-home')
# template_name = 'portfolio/home.html'  # <app>/<model>_<viewtype>.html
# context_object_name = 'posts'
# ordering = ['-date_posted']


@login_required
def crypto_history_file_load(request):
	if request.method == 'POST':
		print(f"Request User: {request.user}")
		print(f"Request FILES: {request.FILES}")
		form = CryptoHistoryUploadForm(request.POST, request.FILES)
		if form.is_valid():
			# Drop any existing history files.
			exist_files = Historyfile.objects.filter(user=request.user)
			for e in exist_files:
				#e_file = os.path.join(settings.MEDIA_ROOT, str(e.upload_file))
				e_file = str(e.upload_file)
				print(f"File located at {e_file}")
				# Delete the physical file
				#if os.path.exists(e_file):
				#	os.remove(e_file)
				if default_storage.exists(e_file):
					default_storage.delete(e_file)
				# delete the database entry.
				e.delete()
			crypto_history = form.save(commit=False)
			crypto_history.user = request.user
			# print(f"crypto_history: {crypto_history}")
			# t_file = f"{crypto_history.upload_file}"
			# crypto_history.original_filename = f"{t_file}"
			# print(f"Not sure: {t_file}")
			# new_filename = f"{request.user.username}_{t_file}"
			# crypto_history.upload_file = os.path.join(settings.MEDIA_ROOT, str(new_filename))
			# print(f"Not sure: {crypto_history.upload_file.name}")
			crypto_history.save()
			#nfile = os.path.join(settings.MEDIA_ROOT, str(crypto_history.upload_file))
			nfile = str(crypto_history.upload_file)
			print(f"Crypto History Filename: {nfile}")
			# Now let's read the file into a database.
			loader_load_home(request, nfile)

			return redirect('portfolio-home')
	else:
		print("Initial read of the form")
		form = CryptoHistoryUploadForm()
	return render(request, 'loader/crypto_load.html', {'form': form})