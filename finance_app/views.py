from django.shortcuts import render

# Create your views here.
from django.shortcuts import render, redirect
from .models import Transaction,Debit
from django.db.models import Sum
from datetime import date
from datetime import timedelta
from collections import defaultdict
import calendar

#Dahboard View
def dashboard(request):
    transactions = Transaction.objects.all().order_by('-date')
    recent_transactions = transactions[:5]

    income = Transaction.objects.filter(type='income').aggregate(Sum('amount'))['amount__sum'] or 0
    expenses = Transaction.objects.filter(type='expense').aggregate(Sum('amount'))['amount__sum'] or 0

    balance = income - expenses

    debits = Debit.objects.filter(paid=False).aggregate(Sum('amount'))['amount__sum'] or 0

    # Chart Data
    months = []
    income_data = []
    expense_data = []

    for i in range(1, 13):
        months.append(calendar.month_abbr[i])

        income_sum = Transaction.objects.filter(type='income', date__month=i).aggregate(Sum('amount'))['amount__sum'] or 0
        expense_sum = Transaction.objects.filter(type='expense', date__month=i).aggregate(Sum('amount'))['amount__sum'] or 0

        income_data.append(float(income_sum))
        expense_data.append(float(expense_sum))

    # ADD CATEGORY DATA (FOR PIE CHART)
    from collections import defaultdict
    category_data = defaultdict(float)

    for t in Transaction.objects.filter(type='expense'):
        category_data[t.category] += float(t.amount)

    category_labels = list(category_data.keys())
    category_values = list(category_data.values())

    context = {
        'balance': balance,
        'income': income,
        'expenses': expenses,
        'debits': debits,

        'months': months,
        'income_data': income_data,
        'expense_data': expense_data,
        'recent_transactions': recent_transactions,
        'category_labels': category_labels,
        'category_values': category_values,

        'date': date.today()
    }

    return render(request, 'dashboard.html', context)


# =============================
# Expenses View
def expenses(request):

    today = date.today()
    daily_total = Transaction.objects.filter(
        type='expense', date=today
    ).aggregate(Sum('amount'))['amount__sum'] or 0

    monthly_total = Transaction.objects.filter(
        type='expense', date__month=today.month
    ).aggregate(Sum('amount'))['amount__sum'] or 0

    yearly_total = Transaction.objects.filter(
        type='expense', date__year=today.year
    ).aggregate(Sum('amount'))['amount__sum'] or 0

    # DAILY GRAPH
   
    days, amounts = [], []

    for i in range(6, -1, -1):
        day = today - timedelta(days=i)

        total = Transaction.objects.filter(
            type='expense', date=day
        ).aggregate(Sum('amount'))['amount__sum'] or 0

        days.append(day.strftime("%d %b"))
        amounts.append(float(total))


   
    # MONTHLY GRAPH
    
    months, monthly_expenses = [], []

    for i in range(1, 13):
        months.append(calendar.month_abbr[i])

        total = Transaction.objects.filter(
            type='expense',
            date__month=i,
            date__year=today.year
        ).aggregate(Sum('amount'))['amount__sum'] or 0

        monthly_expenses.append(float(total))


    
    # YEARLY GRAPH
    
    years, yearly_expenses = [], []

    for y in range(today.year - 4, today.year + 1):
        total = Transaction.objects.filter(
            type='expense', date__year=y
        ).aggregate(Sum('amount'))['amount__sum'] or 0

        years.append(str(y))
        yearly_expenses.append(float(total))


   
    # CATEGORY ANALYSIS
   
    def get_category_data(queryset):
        data = defaultdict(float)

        for t in queryset:
            data[t.category] += float(t.amount)

        labels = list(data.keys())
        values = list(data.values())

        total = sum(values) if values else 1
        percent = [round((v/total)*100) for v in values]

        return labels, values, percent


    daily_qs = Transaction.objects.filter(type='expense', date=today)
    monthly_qs = Transaction.objects.filter(type='expense', date__month=today.month)
    yearly_qs = Transaction.objects.filter(type='expense', date__year=today.year)

    daily_cat_labels, daily_cat_values, daily_cat_percent = get_category_data(daily_qs)
    monthly_cat_labels, monthly_cat_values, monthly_cat_percent = get_category_data(monthly_qs)
    yearly_cat_labels, yearly_cat_values, yearly_cat_percent = get_category_data(yearly_qs)


   
    # WEEKLY COMPARISON
   
    start_of_week = today - timedelta(days=today.weekday())
    last_week_start = start_of_week - timedelta(days=7)
    last_week_end = start_of_week - timedelta(days=1)

    this_week_total = Transaction.objects.filter(
        type='expense', date__gte=start_of_week
    ).aggregate(Sum('amount'))['amount__sum'] or 0

    last_week_total = Transaction.objects.filter(
        type='expense',
        date__gte=last_week_start,
        date__lte=last_week_end
    ).aggregate(Sum('amount'))['amount__sum'] or 0


   
    # BUDGET
   
    budget_limit = 10000
    budget_percent = int((monthly_total / budget_limit) * 100) if budget_limit else 0


    # CONTEXT
  
    context = {
        "daily_total": daily_total,
        "monthly_total": monthly_total,
        "yearly_total": yearly_total,

        "days": days,
        "amounts": amounts,

        "months": months,
        "monthly_expenses": monthly_expenses,

        "years": years,
        "yearly_expenses": yearly_expenses,

        "daily_cat_labels": daily_cat_labels,
        "daily_cat_values": daily_cat_values,
        "daily_cat_percent": daily_cat_percent,

        "monthly_cat_labels": monthly_cat_labels,
        "monthly_cat_values": monthly_cat_values,
        "monthly_cat_percent": monthly_cat_percent,

        "yearly_cat_labels": yearly_cat_labels,
        "yearly_cat_values": yearly_cat_values,
        "yearly_cat_percent": yearly_cat_percent,

        "this_week_total": this_week_total,
        "last_week_total": last_week_total,

        "budget_limit": budget_limit,
        "budget_percent": budget_percent,
    }

    return render(request, "expenses.html", context)
# =============================
# Transactions View

def transactions(request):
        transactions = Transaction.objects.all().order_by('-date')

        return render(request, 'transactions.html', {
        'transactions': transactions
            })
# =============================


def delete_transaction(request, id):

   Transaction.objects.get(id=id).delete()

   return redirect('transactions')

# =============================
# Debits Views
def debits(request):

    status = request.GET.get("status", "all")

    debits = Debit.objects.all()

    today = date.today()

    if status == "pending":
        debits = debits.filter(paid=False)

    elif status == "paid":
        debits = debits.filter(paid=True)

    elif status == "overdue":
        debits = debits.filter(paid=False, due_date__lt=today)

    total_debits = Debit.objects.count()

    total_pending = Debit.objects.filter(paid=False).aggregate(
        Sum("amount")
    )["amount__sum"] or 0

    total_paid = Debit.objects.filter(paid=True).aggregate(
        Sum("amount")
    )["amount__sum"] or 0

    context = {

        "debits": debits,
        "total_debits": total_debits,
        "total_pending": total_pending,
        "total_paid": total_paid,
        "status": status,

        "pending_count": Debit.objects.filter(paid=False).count(),
        "paid_count": Debit.objects.filter(paid=True).count(),
        "overdue_count": Debit.objects.filter(
            paid=False, due_date__lt=today
        ).count()

    }

    return render(request, "debits.html", context)



def add_debit(request):

    if request.method == "POST":

        name = request.POST['name']
        amount = request.POST['amount']
        due_date = request.POST['due_date']
        recurring = request.POST['recurring']

        Debit.objects.create(
            name=name,
            amount=amount,
            due_date=due_date,
            recurring=recurring
        )

    return redirect('debits')



def delete_debit(request, id):

    Debit.objects.get(id=id).delete()

    return redirect('debits')



def mark_paid(request, id):

    debit = Debit.objects.get(id=id)

    debit.paid = True

    debit.save()

    return redirect('debits')