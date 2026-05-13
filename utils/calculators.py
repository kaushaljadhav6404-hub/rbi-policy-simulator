# utils/calculators.py

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