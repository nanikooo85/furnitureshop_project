from django.db import models
from django.db import models
from django.contrib.auth.models import AbstractUser


# ====================================================
# CustomUser მოდელი (გაფართოებული მომხმარებელი)
# ====================================================
class CustomUser(AbstractUser):
    # დამატებითი ველები
    phone = models.CharField(max_length=15, unique=True, blank=True, null=True, verbose_name="მობილურის ნომერი")
    address = models.CharField(max_length=255, blank=True, verbose_name="მისამართი")
    birth_date = models.DateField(blank=True, null=True, verbose_name="დაბადების თარიღი")

    # შეგიძლიათ დაამატოთ სხვა ველებიც თუ დავალება მოითხოვს

    class Meta:
        verbose_name = "Custom User"
        verbose_name_plural = "Custom Users"

    # მეთოდი get_full_name() მოთხოვნილია დავალებით
    def get_full_name(self):
        return f"{self.first_name} {self.last_name}"

    def __str__(self):
        return self.username
# Create your models here.
