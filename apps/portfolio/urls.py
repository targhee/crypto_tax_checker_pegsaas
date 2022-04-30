from django.contrib.auth.decorators import login_required, permission_required
from django.urls import path
from .views import (
    AllTransactionListView,
    DuplicatesListView,
    NoMatchesListView,
    TransactionDetailView,
)
from . import views

urlpatterns = [
    path('', login_required(AllTransactionListView.as_view()), name='portfolio-home'),
    path('duplicates/', login_required(DuplicatesListView.as_view()), name='duplicates-view'),
    path('no-matches/', login_required(NoMatchesListView.as_view()), name='no-matches-view'),
    path('about/', views.about, name='portfolio-about'),
]
