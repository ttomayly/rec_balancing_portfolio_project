import streamlit as st
import plotly.express as px
import session_state as ss
import datetime
import model
import pip

pip.main(["install", "openpyxl"])


# functions
def show_rec_if_no_cl():
    st.subheader("Managing assets")
    for i in range(balanced_model.shape[0] - 2):  # doesn't include cash and bonds
        st.write(balanced_model.iloc[i][0], ": ")
        for key, value in balanced_model.iloc[i][1].items():
            st.write("Buy from ", 0, "to ", value, "of", key)
        st.write("---")

    st.write(balanced_model.iloc[-2][0])
    for key, value in balanced_model.iloc[-2][1].items():
        st.write("Buy from ", 0, "to ", value, "of", key)

    st.write("---")
    st.write("Deposit from ", 0, "to ", int(balanced_model.iloc[-1][1]['cash']))


def show_rec_if_cl():
    st.subheader("Managing assets")
    assets_types = set()
    used = set()
    for i in range(balanced_model.shape[0] - 1):
        st.write(balanced_model.iloc[i][0], ": ")
        stocks = balanced_model.iloc[i][1]
        for key, value in stocks.items():
            if key in session_state.cl_assets:
                used.add(key)
                index = session_state.cl_assets.index(key)
                bought_amount = session_state.cl_units[index]
                if bought_amount > value:
                    st.write("Sell from ", bought_amount, "to ", value, "of", key)
                elif bought_amount < value:
                    st.write("Buy from ", bought_amount, "to ", value, "of", key)
                else:
                    st.write("Keep the same amount of", key)
            else:
                st.write("Buy from ", 0, "to ", value, "of", key)
        if balanced_model.iloc[i][0] in cl_stocks:
            st_type = cl_stocks[balanced_model.iloc[i][0]]
            for j in range(len(st_type)):
                index = session_state.cl_assets.index(st_type[j])
                if session_state.cl_assets[index] not in used:
                    st.write("Sell from ", session_state.cl_units[index], "to ", 0, "of",
                             session_state.cl_assets[index])
        assets_types.add(balanced_model.iloc[i][0])
        st.write("---")

    for key, value in cl_stocks.items():
        if key not in assets_types and value:
            st.write(key, ": ")
            for i in range(len(value)):
                index = session_state.cl_assets.index(value[i])
                st.write("Sell from ", session_state.cl_units[index], "to ", 0, "of",
                         session_state.cl_assets[index])
            st.write("---")

    st.write("Deposit from ", int(deposit), "to ", int(balanced_model.iloc[-1][1]['cash']))


def show_pie_chart(values, names, df):
    fig = px.pie(df, values=values, names=names, height=300, width=200,
                 color=names, color_discrete_map={'Large Cap': 'lightcyan', 'Small or Mid Cap': 'cyan',
                                                  'Foreign': 'royalblue', 'Bonds': 'darkblue', 'Cash': 'blue',
                                                  'TNX': 'lightcyan', 'IRX': 'cyan',
                                                  'TYX': 'royalblue', 'FVX': 'darkblue'})
    fig.update_layout(margin=dict(l=20, r=20, t=30, b=0), )
    st.plotly_chart(fig, use_container_width=True)


def show_pies_cl():
    st.subheader("Recommendation on balancing")
    col_pie1, col_pie2 = st.columns(2)
    with col_pie1:
        cl_df_assets_ch = cl_df_assets.loc[lambda cl_df_assets: cl_df_assets['client'] != 0]
        st.markdown("**Your allocation of assets**")
        show_pie_chart('client', 'assets', cl_df_assets_ch)
    with col_pie2:
        rec_portfolio_stocks_ch = rec_portfolio_stocks.loc[
            lambda rec_portfolio_stocks: rec_portfolio_stocks[profile] != 0]
        st.markdown("**Recommended allocation of assets**")
        show_pie_chart(profile, 'assets', rec_portfolio_stocks_ch)

    rec_portfolio_bonds_ch = rec_portfolio_bonds.loc[lambda rec_portfolio_bonds: rec_portfolio_bonds[profile] != 0]
    rec_portfolio_bonds_ch = rec_portfolio_bonds_ch.reset_index(drop=True)
    cl_df_bonds_ch = cl_df_bonds.loc[lambda cl_df_bonds: cl_df_bonds['client'] != 0]
    if rec_portfolio_bonds_ch.shape[0]:
        rec_portfolio_bonds_ch = rec_portfolio_bonds_ch.drop(labels=rec_portfolio_bonds_ch.shape[0] - 1, axis=0)
    if cl_df_bonds_ch.shape[0] and rec_portfolio_bonds_ch.shape[0]:
        with col_pie1:
            st.markdown("**Your allocation of bonds**")
            show_pie_chart('client', 'bonds', cl_df_bonds_ch)
        with col_pie2:
            st.markdown("**Recommended allocation of bonds**")
            show_pie_chart(profile, 'bonds', rec_portfolio_bonds_ch)
    elif not cl_df_bonds_ch.shape[0] and rec_portfolio_bonds_ch.shape[0]:
        with col_pie1:
            st.markdown("**Your allocation of bonds**")
            st.write("You do not have bonds")
        with col_pie2:
            st.markdown("**Recommended allocation of bonds**")
            show_pie_chart(profile, 'bonds', rec_portfolio_bonds_ch)


def show_pies_no_cl():
    st.subheader("Recommendation on allocation")
    col_pie1, col_pie2 = st.columns(2)
    with col_pie1:
        rec_portfolio_stocks_ch = rec_portfolio_stocks.loc[
            lambda rec_portfolio_stocks: rec_portfolio_stocks[profile] != 0]
        st.markdown("**Recommended allocation of assets**")
        show_pie_chart(profile, 'assets', rec_portfolio_stocks_ch)
    with col_pie2:
        rec_portfolio_bonds_ch = rec_portfolio_bonds.loc[lambda rec_portfolio_bonds: rec_portfolio_bonds[profile] != 0]
        rec_portfolio_bonds_ch = rec_portfolio_bonds_ch.drop(labels=rec_portfolio_bonds_ch.shape[0] - 1, axis=0)
        st.markdown("**Recommended allocation of bonds**")
        show_pie_chart(profile, 'bonds', rec_portfolio_bonds_ch)


def show_performance_cl():
    st.subheader("Performance")
    cl_ret, cl_vol = model.get_value(session_state.cl_assets, session_state.cl_units)
    rec_assets, rec_units = model.convert(balanced_model)
    rec_ret, rec_vol = model.get_value(rec_assets, rec_units)
    cld1, cld2 = st.columns(2)
    with cld1:
        st.markdown("**Your portfolio**")
        st.write("Return: ", round(cl_ret * 100, 2), "%")
        st.write("Volatility: ", round(cl_vol * 100, 2), "%")
    with cld2:
        st.markdown("**Recommended portfolio**")
        st.write("Return: ", round(rec_ret * 100, 2), "%")
        st.write("Volatility: ", round(rec_vol * 100, 2), "%")


def show_performance_no_cl():
    st.subheader("Recommended portfolio performance")
    rec_assets, rec_units = model.convert(balanced_model)
    rec_ret, rec_vol = model.get_value(rec_assets, rec_units)
    st.write("Return: ", round(rec_ret * 100, 2))
    st.write("Volatility: ", round(rec_vol * 100, 2))


def show_pies():
    if session_state.cl_assets:
        show_pies_cl()
    else:
        show_pies_no_cl()


def show_performance():
    if session_state.cl_assets:
        show_performance_cl()
    else:
        show_performance_no_cl()


def show_recommendations():
    if session_state.cl_assets:
        show_rec_if_cl()
    else:
        show_rec_if_no_cl()


# main page
st.title("Recommendations on portfolio balancing")

# sidebar
st.sidebar.header('Input current portfolio and your risk profile')

deposit = st.sidebar.text_input("How much money do you hold as deposit?(in $)")
if deposit:
    deposit = float(deposit)
else:
    deposit = 0

acquisition_date = st.sidebar.date_input("What\'s the acquisition date of portfolio?", value=datetime.date(2016, 1, 1))

col1, col2 = st.sidebar.columns(2)
with col1:
    asset = st.selectbox("Ticker", (model.all_stocks['Ticker']))
    recommend = st.checkbox("Recommend new stocks")
with col2:
    unit = st.number_input("Number of units", step=1)

session_state = ss.get(cl_assets=[], cl_units=[], add_button=False)
with col2:
    session_state.add_button = st.button("Add")
if session_state.add_button:
    if asset in session_state.cl_assets:
        ind = session_state.cl_assets.index(asset)
        session_state.cl_units[ind] += unit
    else:
        session_state.cl_assets.append(asset)
        session_state.cl_units.append(unit)

st.sidebar.write("---")
risk_profile = st.sidebar.selectbox('Risk profile', ('conservative', 'moderately conservative',
                                                     'moderate', 'moderately aggressive', 'aggressive'))

horizon = st.sidebar.slider(label='Horizon of investment', min_value=0, max_value=20, step=1)

money = st.sidebar.text_input("Money to invest(in $)")
if money:
    money = float(money)
else:
    money = 0


# calculations
calc_button = st.sidebar.button("Calculate")

if calc_button:
    model.recommend = recommend
    model.start_date = acquisition_date
    model.deposit = deposit

    if session_state.cl_assets:
        cl_stocks, init_portfolio_value, cl_df_assets, cl_df_bonds = \
            model.get_client_assets(session_state.cl_assets, session_state.cl_units)

    profile, rec_portfolio_stocks, rec_portfolio_bonds = model.get_recommended(risk_profile, horizon)

    show_pies()

    balanced_model = model.get_balancing(session_state.cl_assets, session_state.cl_units, risk_profile, horizon, money)

    show_performance()
    show_recommendations()

st.markdown("Disclaimer: Information on this page is provided purely for **entertaining and informal** use and"
            " **does not represent advice** on finances, investments, or business. The website's author is not"
            " qualified to offer business, financial, or investment advice.")
