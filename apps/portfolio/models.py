from django.db import models
from django.utils import timezone
from django.contrib.auth.models import User
from django.urls import reverse

from crypto_tax_checker import settings

class Transaction(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    timestamp = models.DateTimeField()
    trade_type = models.CharField(max_length=20, unique=False)
    in_asset = models.CharField(max_length=10, unique=False)
    in_qty = models.FloatField()
    out_asset = models.CharField(max_length=10, unique=False)
    out_qty = models.FloatField()
    fee_asset = models.CharField(max_length=10, unique=False)
    fee_qty = models.FloatField()
    tx_id = models.CharField(max_length=200, unique=False)
    exchange = models.CharField(max_length=20)
    part = models.IntegerField()
    reconciled = models.BooleanField()
    match_num = models.CharField(max_length=200)
    duplicate = models.BooleanField()

    def __str__(self):
        return " ".join([self.user.username, self.trade_type,
                         str(self.timestamp),
                         "IN:", str(self.in_asset), str(self.in_qty),
                         "OUT:", str(self.out_asset), str(self.out_qty),
                         "Exchange:", str(self.exchange)])

    def get_absolute_url(self):
        return reverse('transaction-detail', kwargs={'pk': self.pk})