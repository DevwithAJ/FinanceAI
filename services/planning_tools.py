from math import ceil

MERCHANT_RULES = {
    'Dining': ['swiggy','zomato','restaurant','cafe','dominos','pizza'],
    'Groceries': ['blinkit','zepto','bigbasket','grocery','mart','dmart'],
    'Transport': ['uber','ola','rapido','metro','irctc','railway','petrol','fuel'],
    'Shopping': ['amazon','flipkart','myntra','ajio','meesho'],
    'Utilities': ['electricity','bescom','recharge','jio','airtel','vi ','broadband','gas bill'],
    'Entertainment': ['netflix','spotify','hotstar','cinema','bookmyshow'],
    'Healthcare': ['pharmacy','apollo','hospital','clinic','1mg','pharmeasy'],
    'Education': ['college','university','course','udemy','school','tuition'],
    'Housing': ['rent','landlord'],
    'EMI / Debt': ['emi','loan repayment'],
    'Insurance': ['insurance','lic premium'],
}

def smart_category(description, fallback='Other Expense'):
    text=(description or '').lower()
    for category, words in MERCHANT_RULES.items():
        if any(w in text for w in words): return category
    return fallback

def what_if(income, expenses, income_change=0, expense_change=0, discretionary_cut=0, emi_change=0):
    income=max(0,float(income)); expenses=max(0,float(expenses))
    new_income=max(0,income+float(income_change))
    new_expenses=max(0,expenses+float(expense_change)-max(0,float(discretionary_cut))+float(emi_change))
    before=income-expenses; after=new_income-new_expenses
    return {'before_income':round(income,2),'before_expense':round(expenses,2),'before_savings':round(before,2),
            'after_income':round(new_income,2),'after_expense':round(new_expenses,2),'after_savings':round(after,2),
            'monthly_improvement':round(after-before,2),'annual_improvement':round((after-before)*12,2),
            'after_savings_rate':round(after/new_income*100,1) if new_income else 0}

def emergency_plan(monthly_expense,current_fund,target_months=6,monthly_contribution=0):
    expense=max(0,float(monthly_expense)); current=max(0,float(current_fund)); months=max(1,float(target_months))
    target=expense*months; gap=max(0,target-current); contribution=max(0,float(monthly_contribution))
    eta=ceil(gap/contribution) if contribution>0 and gap>0 else (0 if gap==0 else None)
    return {'monthly_expense':round(expense,2),'current_fund':round(current,2),'target_months':months,
            'target':round(target,2),'gap':round(gap,2),'coverage_months':round(current/expense,1) if expense else 0,
            'monthly_contribution':round(contribution,2),'months_to_target':eta}
