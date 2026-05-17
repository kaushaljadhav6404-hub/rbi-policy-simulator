import streamlit as st
import pandas as pd
import plotly.express as px
from utils.calculators import calculate_emi, calculate_bond_price 

# 1. Set up the page layout
st.set_page_config(page_title="RBI Policy Simulator", layout="wide")

# 2. Add a Navigation sidebar
# -> NEW: Added "Policy Simulator" to the navigation menu
st.sidebar.title("Navigation")
page = st.sidebar.radio("Go to", ["Home", "EMI Calculator", "Bond Price Simulator", "Sector Impact", "Policy Simulator"])

# ---------------------------------------------------
# SECTION 1 — HOME PAGE
# ---------------------------------------------------
if page == "Home":
    st.title("🏦 RBI Monetary Policy Impact Simulator")
    st.markdown("### A quantitative dashboard analyzing the impact of interest rate cycles.")
    st.divider()
    
    col1, col2 = st.columns(2)
    with col1:
        st.subheader("What is the Repo Rate?")
        st.write("The Repo Rate is the rate at which the Reserve Bank of India (RBI) lends money to commercial banks.")
        st.info("**Current Benchmark Repo Rate:** 5.25%")
    with col2:
        st.subheader("Why It Matters")
        st.write("- **For Borrowers:** Higher rates mean higher EMIs.")
        st.write("- **For Investors:** Changes affect bond prices and stock markets.")
        st.write("- **For Banks:** Impacts their profit margins (NIM).")

# ---------------------------------------------------
# SECTION 2 — EMI CALCULATOR
# ---------------------------------------------------
elif page == "EMI Calculator":
    st.title("📊 Loan EMI Impact Simulator")
    st.write("Simulate how an RBI rate hike or cut trickles down to consumer borrowing costs.")
    
    col1, col2, col3 = st.columns(3)
    with col1:
        principal = st.number_input("Loan Amount (₹)", min_value=100000, value=5000000, step=100000)
    with col2:
        current_rate = st.number_input("Current Bank Interest Rate (%)", min_value=1.0, value=8.5, step=0.1)
    with col3:
        tenure = st.number_input("Loan Tenure (Years)", min_value=1, value=15, step=1)
        
    st.divider()
    st.subheader("Simulate RBI Policy Action & Bank Transmission")
    
    # Original slider for RBI action
    rate_change_bps = st.slider("RBI Repo Rate Change (in Basis Points)", min_value=-200, max_value=200, value=50, step=25)
    
    # NEW SLIDER: Transmission Efficiency
    transmission_pct = st.slider(
        "Bank Transmission Efficiency (%)", 
        min_value=0, max_value=100, value=70, step=10,
        help="100% means the bank passes the entire RBI rate change to the customer. 70% means they absorb a portion of it to protect loan growth or margins."
    )
    
    # New Math: Calculate how much of the rate actually reaches the customer
    actual_rate_change = (rate_change_bps / 100) * (transmission_pct / 100)
    new_rate = current_rate + actual_rate_change
    
    old_emi = calculate_emi(principal, current_rate, tenure)
    new_emi = calculate_emi(principal, new_rate, tenure)
    
    # Smart text box explaining the real-world bank action
    st.info(f"🏦 **Real-World Bank Action:** The RBI changed rates by **{rate_change_bps} bps**, but because transmission is **{transmission_pct}%**, the bank only adjusted the customer's loan rate by **{actual_rate_change * 100:.0f} bps**.")
    
    st.write(f"**New Estimated Bank Interest Rate:** {new_rate:.2f}%")
    
    res_col1, res_col2, res_col3 = st.columns(3)
    res_col1.metric("Original Monthly EMI", f"₹{old_emi:,.0f}")
    res_col2.metric("New Monthly EMI", f"₹{new_emi:,.0f}", f"{new_emi - old_emi:,.0f} change")
    res_col3.metric("Extra Yearly Outflow", f"₹{(new_emi - old_emi) * 12:,.0f}")
# ---------------------------------------------------
# SECTION 3 — BOND PRICE SIMULATOR
# ---------------------------------------------------
elif page == "Bond Price Simulator":
    st.title("📉 Bond Price Impact Simulator")
    st.write("Understand the inverse relationship between market interest rates (yields) and bond prices.")
    
    col1, col2, col3 = st.columns(3)
    with col1:
        face_value = st.number_input("Bond Face Value (₹)", min_value=100, value=1000, step=100)
    with col2:
        coupon_rate = st.number_input("Annual Coupon Rate (%)", min_value=1.0, value=7.0, step=0.5)
    with col3:
        years = st.number_input("Years to Maturity", min_value=1, value=10, step=1)
        
    st.divider()
    
    st.subheader("Simulate Market Yield Change")
    yield_change_bps = st.slider("Market Yield Change (in Basis Points)", min_value=-200, max_value=200, value=50, step=25)
    
    current_yield = coupon_rate
    new_yield = current_yield + (yield_change_bps / 100)
    
    old_price = calculate_bond_price(face_value, coupon_rate, years, current_yield)
    new_price = calculate_bond_price(face_value, coupon_rate, years, new_yield)
    
    res_col1, res_col2 = st.columns(2)
    res_col1.metric("Original Bond Price (At Par)", f"₹{old_price:,.2f}")
    res_col2.metric("New Bond Price", f"₹{new_price:,.2f}", f"{new_price - old_price:,.2f} value change")

    st.divider()
    st.subheader("Visualizing the Price-Yield Curve")
    
    yields_list = []
    prices_list = []
    for y in range(20, 125, 5): 
        y_decimal = y / 10.0
        yields_list.append(y_decimal)
        prices_list.append(calculate_bond_price(face_value, coupon_rate, years, y_decimal))
        
    df = pd.DataFrame({"Market Yield (%)": yields_list, "Bond Price (₹)": prices_list})
    fig = px.line(df, x="Market Yield (%)", y="Bond Price (₹)", title="Bond Price Curve")
    fig.add_vline(x=new_yield, line_dash="dash", line_color="red", annotation_text="New Market Yield")
    st.plotly_chart(fig, use_container_width=True)

# ---------------------------------------------------
# SECTION 4 — SECTOR IMPACT
# ---------------------------------------------------
elif page == "Sector Impact":
    st.title("🏢 Sector-Wise Equity Impact")
    st.write("Analyze how an RBI rate hike historically impacts different sectors of the Indian economy.")
    st.divider()
    
    sector_data = {
        "Sector": ["Banking", "NBFCs", "Real Estate", "Automobile", "FMCG", "IT / Tech"],
        "Impact of Rate Hike": ["Neutral to Positive", "Negative", "Highly Negative", "Negative", "Neutral", "Neutral"],
        "Financial Rationale": [
            "Banks reprice floating-rate loans faster than fixed deposits, temporarily boosting Net Interest Margins (NIM).",
            "Cost of wholesale borrowing rises. Cannot easily pass costs to sub-prime borrowers, compressing margins.",
            "Higher home loan EMIs heavily reduce housing demand and delay new project launches.",
            "Auto loans become expensive, dampening consumer discretionary demand for vehicles.",
            "Non-discretionary spending. Consumers still buy daily necessities regardless of the repo rate.",
            "Largely debt-free and export-driven. Margins are more affected by US Fed rates and Rupee depreciation."
        ]
    }
    
    df_sectors = pd.DataFrame(sector_data)
    st.dataframe(df_sectors, use_container_width=True, hide_index=True)
    st.info("💡 **Key Macro Insight:** Historically, there is a stark divergence in how rate hikes affect Banks vs. NBFCs. Banks typically benefit from a lag in repricing deposits due to cheap CASA bases, whereas NBFCs face immediate margin compression due to their reliance on wholesale market borrowing.")

# ---------------------------------------------------
# SECTION 5 — POLICY SIMULATOR (NEW)
# ---------------------------------------------------
elif page == "Policy Simulator":
    st.title("⚖️ Central Bank Scenario Simulator")
    st.write("Select a monetary policy stance to see the cascading macroeconomic effects across the economy.")
    st.divider()

    # Create clickable radio buttons for the user to choose a scenario
    stance = st.radio(
        "Select RBI Monetary Policy Stance:",
        ["🦅 Hawkish (Contractionary)", "⏸️ Neutral (Status Quo)", "🕊️ Dovish (Expansionary)"],
        horizontal=True
    )

    st.divider()

    # Logic to change the text based on the user's selection
    if "Hawkish" in stance:
        rate_action = "+ 50 bps (Rate Hike)"
        inflation = "Cooling (Decreasing)"
        growth = "Slowing Down"
        bonds = "Yields Up / Prices Down"
        liquidity = "Tightening (Absorbing money)"
        best_sector = "Banking (temporarily)"
        worst_sector = "Real Estate & Auto"

    elif "Neutral" in stance:
        rate_action = "0 bps (Unchanged)"
        inflation = "Stable / Monitored"
        growth = "Steady"
        bonds = "Range-bound"
        liquidity = "Balanced"
        best_sector = "FMCG & IT (Defensives)"
        worst_sector = "None (Focus shifts to earnings)"

    else: # Dovish
        rate_action = "- 50 bps (Rate Cut)"
        inflation = "Rising (Potential Risk)"
        growth = "Accelerating (Stimulated)"
        bonds = "Yields Down / Prices Up"
        liquidity = "Expanding (Injecting money)"
        best_sector = "Real Estate & Infra"
        worst_sector = "Banking (Margin compression)"

    # Display the results using Streamlit columns and metrics
    st.subheader(f"Macroeconomic Cascading Impact: {stance.split(' ')[1]}")
    
    col1, col2 = st.columns(2)

    with col1:
        st.metric("Expected Repo Rate Action", rate_action)
        st.metric("Systemic Liquidity", liquidity)
        st.metric("Impact on Bond Market", bonds)
        
    with col2:
        st.metric("Effect on Inflation", inflation)
        st.metric("Effect on GDP Growth", growth)
        st.metric("Equities: Most Pressured Sector", worst_sector)

    st.divider()
    st.info("💡 **Key Macro Insight:** Central banks rarely operate in absolutes. A governor might keep rates 'Neutral' but provide a 'Hawkish commentary' to manage market expectations without crashing liquidity. Institutional investors always separate the *rate action* from the *policy commentary*.")
