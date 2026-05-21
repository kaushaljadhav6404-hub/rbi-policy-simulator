import pandas as pd
import requests
from bs4 import BeautifulSoup
import re

def calculate_emi(principal, annual_rate, tenure_years):
    """
    Calculates the monthly Equated Monthly Installment (EMI).
    """
    if annual_rate == 0:
        return principal / (tenure_years * 12)
        
    monthly_rate = (annual_rate / 12) / 100
    tenure_months = tenure_years * 12
    
    emi = principal * monthly_rate * (((1 + monthly_rate) ** tenure_months) / (((1 + monthly_rate) ** tenure_months) - 1))
    return emi


def calculate_bond_price(face_value, coupon_rate, years_to_maturity, market_rate):
    """
    Calculates the bond price using the Present Value of future cash flows.
    """
    if market_rate <= 0:
        return face_value
        
    coupon_payment = face_value * (coupon_rate / 100)
    market_rate_decimal = market_rate / 100
    
    bond_price = 0
    for year in range(1, years_to_maturity + 1):
        bond_price += coupon_payment / ((1 + market_rate_decimal) ** year)
        
    bond_price += face_value / ((1 + market_rate_decimal) ** years_to_maturity)
    return bond_price


def fetch_live_repo_rate():
    """
    Scrapes the official RBI website for the live Policy Repo Rate.
    Includes a 'Graceful Degradation' fallback so the app never crashes.
    """
    fallback_rate = 6.50 
    
    try:
        url = "https://www.rbi.org.in/"
        headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64)'}
        response = requests.get(url, headers=headers, timeout=5)
        soup = BeautifulSoup(response.text, 'html.parser')
        
        rate_text = soup.find(string=re.compile("Policy Repo Rate", re.IGNORECASE))
        
        if rate_text:
            parent_div = rate_text.find_parent('div') or rate_text.find_parent('tr')
            if parent_div:
                full_text = parent_div.get_text()
                match = re.search(r'(\d+\.\d+)', full_text)
                if match:
                    return float(match.group(1))
                    
        return fallback_rate
        
    except Exception as e:
        return fallback_rate


def generate_amortization_schedule(principal, old_annual_rate, new_annual_rate, tenure_years):
    """
    Generates a full month-by-month loan repayment schedule.
    Compares the Old Rate scenario vs. the New Rate scenario.
    """
    tenure_months = int(tenure_years * 12)
    old_monthly_rate = (old_annual_rate / 12) / 100
    new_monthly_rate = (new_annual_rate / 12) / 100

    old_emi = principal * old_monthly_rate * (((1 + old_monthly_rate) ** tenure_months) / (((1 + old_monthly_rate) ** tenure_months) - 1))
    new_emi = principal * new_monthly_rate * (((1 + new_monthly_rate) ** tenure_months) / (((1 + new_monthly_rate) ** tenure_months) - 1))

    schedule = []
    old_balance = principal
    new_balance = principal

    for month in range(1, tenure_months + 1):
        old_interest = old_balance * old_monthly_rate
        old_principal_payment = old_emi - old_interest
        old_balance = old_balance - old_principal_payment

        new_interest = new_balance * new_monthly_rate
        new_principal_payment = new_emi - new_interest
        new_balance = new_balance - new_principal_payment

        schedule.append({
            "Month": month,
            "Old EMI (₹)": round(old_emi, 2),
            "New EMI (₹)": round(new_emi, 2),
            "Monthly EMI Impact (₹)": round(new_emi - old_emi, 2), 
            "Old Interest Component (₹)": round(old_interest, 2),
            "New Interest Component (₹)": round(new_interest, 2),
            "Old Remaining Balance (₹)": round(max(0, old_balance), 2),
            "New Remaining Balance (₹)": round(max(0, new_balance), 2)
        })

    return pd.DataFrame(schedule)
