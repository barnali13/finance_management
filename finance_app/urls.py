from django.urls import path
from . import views

urlpatterns = [

    path('', views.dashboard, name='dashboard'),

    path('expenses/', views.expenses, name='expenses'),
    # path('add-transaction/', views.add_transaction, name='add_transaction'),

    # ✅ THIS IS MISSING (YOUR ERROR)
    path('delete-transaction/<int:id>/', views.delete_transaction, name='delete_transaction'),

    path('debits/', views.debits, name='debits'),
    path('add-debit/', views.add_debit, name='add_debit'),
    path('delete-debit/<int:id>/', views.delete_debit, name='delete_debit'),
    path('mark-paid/<int:id>/', views.mark_paid, name='mark_paid'),
    path('transactions/', views.transactions, name='transactions'),
]