from django.db import models


class Transaction(models.Model):

    TYPE_CHOICES = (
        ('income', 'Income'),
        ('expense', 'Expense')
    )
    
    CATEGORY_CHOICES = (
        ('health', 'Healthcare'),
        ('entertainment', 'Entertainment'),
        ('shopping', 'Shopping'),
        ('food', 'Food & Dining'),
        ('travel', 'Travel'),
        ('salary', 'Salary'),
        ('investment', 'Investment')
    )

    type = models.CharField(max_length=10, choices=TYPE_CHOICES)

    amount = models.DecimalField(max_digits=10, decimal_places=2)

    category = models.CharField(max_length=100, choices=CATEGORY_CHOICES)
    payment_mode = models.CharField(max_length=20, choices=[
    ('cash','Cash'),
    ('card','Card')
    ], default='cash')
    description = models.CharField(max_length=200, blank=True)

    date = models.DateField()

    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.type} - {self.amount}"
class Debit(models.Model):

    RECUR_CHOICES = (
        ('monthly', 'Monthly'),
        ('yearly', 'Yearly'),
        ('none', 'None')
    )

    name = models.CharField(max_length=200)

    amount = models.DecimalField(max_digits=10, decimal_places=2)

    due_date = models.DateField()

    recurring = models.CharField(
        max_length=10,
        choices=RECUR_CHOICES,
        default='none'
    )

    paid = models.BooleanField(default=False)

    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.name