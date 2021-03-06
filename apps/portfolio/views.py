from django.shortcuts import render, get_object_or_404
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.contrib.messages.views import SuccessMessageMixin
from django.contrib import messages
from django.contrib.auth.models import User
from django.views.generic import (
    ListView,
    DetailView,
    CreateView,
    UpdateView,
    DeleteView
)
from .models import Transaction

def home(request):
    context = {
        'transactions': Transaction.objects.all()
    }
    return render(request, 'portfolio/transaction_list.html', context)


class AllTransactionListView(LoginRequiredMixin, ListView):
    model = Transaction
    login_url = 'users:login'
    paginate_by = 25
    list_view_type = "Complete"
    num_tx = 0
    text = "This has all the transactions in the uploaded file."

    def get_context_data(self, **kwargs):
        context = super(AllTransactionListView, self).get_context_data(**kwargs)
        context.update( {'list_view_type': self.list_view_type, 'num_tx': self.num_tx,
                         'list_desc': self.text})
        return context

    def get_queryset(self):
        tx = Transaction.objects.all()
        self.num_tx = len(tx)
        #print(f"Number of Transactions = {self.num_tx}")
        return tx


class DuplicatesListView(LoginRequiredMixin, SuccessMessageMixin, ListView):
    model = Transaction
    login_url = 'users:login'
    paginate_by = 25
    list_view_type = "Duplicates"
    num_tx = 0
    text = "\n".join(
        [f"An inspection found some potential duplicates (same timestamp, asset, & quantity)",
         "Transactions that are listed as 'exchange:Manual' are even more suspicious because",
         "they may have been entered in manually by the owner who may have accidentally entered",
         "the same transaction multiple times."])

    def get_context_data(self, **kwargs):
        context = super(DuplicatesListView, self).get_context_data(**kwargs)
        context.update({'list_view_type': self.list_view_type, 'num_tx':self.num_tx,
                        'list_desc': self.text})
        return context

    def get_queryset(self):
        dups = Transaction.objects.filter(duplicate=True)
        self.num_tx = len(dups)
        #print(f"Number of Duplicates = {self.num_dups}")
        return dups


class NoMatchesListView(LoginRequiredMixin, ListView):
    model = Transaction
    login_url = 'users:login'
    paginate_by = 25
    list_view_type = "No Matches"
    text = "\n".join(
        [f"An inspection found some 'Send' transactions could not be matched",
         "    to a 'Receive' transaction.",
         "<p>The following reasons could explain this:</p>\n",
         "<p>1) The coin was sent as payment to someone. In this case, the coin is correctly",
         "   interpreted as a 'Sell' action.</p>\n",
         "<p>2) The coin was sent to another exchange that the tax software was not aware of.",
         "   In this case, upload the other exchange so the matching 'Receive' can be found.</p>",
         "3) The coin was sent to a wallet that you control. In this case, the wallet should",
         "   be added or a manual transaction added so this will not be listed as a sale.",
         "   Be careful using this because if the IRS audits you later and you don't have",
         "   the wallet address or the wallet indicates the coin left the wallet within the",
         "   tax year, you'll be liable for taxes and penalties.",
         "   Remember, for most coins, the blockchain is a complete history of transactions",
         "   that the IRS can verify against your claims.\n",
         ])

    def get_context_data(self, **kwargs):
        context = super(NoMatchesListView, self).get_context_data(**kwargs)
        context.update({'list_view_type': self.list_view_type, 'num_tx': self.num_tx,
                        'list_desc': self.text})
        return context

    def get_queryset(self):
        no_matches = Transaction.objects.filter(match_num="0", trade_type="Send")
        self.num_tx = len(no_matches)
        return no_matches


class TransactionDetailView(DetailView):
    model = Transaction
