from __future__ import unicode_literals

from django.db import models
from django.contrib.auth.models import User

# Create your models here.

class FormD(models.Model):
    cik = models.CharField(max_length=100)
    name = models.CharField(max_length=500)
    year_of_incorp = models.CharField(max_length=30)
    street1 = models.CharField(max_length=100)
    street2 = models.CharField(max_length=100)
    zip_code = models.CharField(max_length=10)
    city = models.CharField(max_length=100)
    state = models.CharField(max_length=10)
    ind_group_type = models.CharField(max_length=100)
    min_investment_accepted = models.IntegerField()
    total_amount_sold = models.IntegerField()
    total_offering_amount = models.IntegerField()
    total_remaining = models.IntegerField()
    has_non_accred = models.BooleanField()
    num_non_accred = models.IntegerField()
    tot_number_investors = models.IntegerField()
    date_added = models.DateField(null=True)


#Model for the profile of a student. This info is gathered when the user creates an account
#and is stored in the database so it can be used without getting the user's info every time
class Analyst(models.Model):
    first_name = models.CharField(max_length=30)
    last_name = models.CharField(max_length=30)
    email = models.CharField(max_length=100)
    user = models.OneToOneField(
        User,
        on_delete=models.CASCADE,
        primary_key=True
    )
