# utils/calculators.py
import pandas as pd
def calculate_emi(principal, annual_rate, tenure_years):
    """
    This function calculates the monthly EMI for a loan.
    """
    # If interest rate is 0, just divide the loan by the total months
    if annual_rate == 0:
        return principal / (tenure_years * 12)
        
    # Convert annual rate to a monthly decimal
    monthly_rate = (annual_rate / 12) / 100
    tenure_months = tenure_years * 12
    
    # The mathematical formula for EMI
    emi = principal * monthly_rate * (((1 + monthly_rate) ** tenure_months) / (((1 + monthly_rate) ** tenure_months) - 1))
    
    return emi



def calculate_bond_price(face_value, coupon_rate, years_to_maturity, market_rate):
    """
    Calculates the bond price using the Present Value of future cash flows.
    Assumes annual coupon payments for simplicity.
    """
    if market_rate <= 0:
        return face_value # Safety check to avoid errors
        
    coupon_payment = face_value * (coupon_rate / 100)
    market_rate_decimal = market_rate / 100
    
    bond_price = 0
    # Calculate Present Value of all annual coupon payments
    for year in range(1, years_to_maturity + 1):
        bond_price += coupon_payment / ((1 + market_rate_decimal) ** year)
        
    # Add Present Value of the face value returned at the end (Maturity)
    bond_price += face_value / ((1 + market_rate_decimal) ** years_to_maturity)
    
    return bond_price

def generate_amortization_schedule(principal, old_annual_rate, new_annual_rate, tenure_years):
    """
    Generates a full month-by-month loan repayment schedule.
    Compares the Old Rate scenario vs. the New Rate scenario.
    """
    tenure_months = tenure_years * 12
    old_monthly_rate = (old_annual_rate / 12) / 100
    new_monthly_rate = (new_annual_rate / 12) / 100

    # Calculate the flat EMIs
    old_emi = principal * old_monthly_rate * (((1 + old_monthly_rate) ** tenure_months) / (((1 + old_monthly_rate) ** tenure_months) - 1))
    new_emi = principal * new_monthly_rate * (((1 + new_monthly_rate) ** tenure_months) / (((1 + new_monthly_rate) ** tenure_months) - 1))

    schedule = []
    old_balance = principal
    new_balance = principal

    # Loop through every month of the loan to calculate the schedule
    for month in range(1, tenure_months + 1):
        # Old Loan Math
        old_interest = old_balance * old_monthly_rate
        old_principal_payment = old_emi - old_interest
        old_balance = old_balance - old_principal_payment

        # New Loan Math
        new_interest = new_balance * new_monthly_rate
        new_principal_payment = new_emi - new_interest
        new_balance = new_balance - new_principal_payment

        # Save this month's data into a dictionary (like an Excel row)
        schedule.append({
            "Month": month,
            "Old EMI (₹)": round(old_emi, 2),
            "New EMI (₹)": round(new_emi, 2),
            "Monthly EMI Impact (₹)": round(new_emi - old_emi, 2), # The exact column you requested!
            "Old Interest Component (₹)": round(old_interest, 2),
            "New Interest Component (₹)": round(new_interest, 2),
            "Old Remaining Balance (₹)": round(max(0, old_balance), 2),
            "New Remaining Balance (₹)": round(max(0, new_balance), 2)
        })

    # Convert the list of rows into a Pandas DataFrame (Data Table)
    return pd.DataFrame(schedule)
