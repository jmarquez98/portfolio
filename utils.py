import pandas as pd
import pandas_market_calendars as mcal
import yfinance as yf
from datetime import datetime


def get_cedears_conversion():
    conversiones = pd.read_excel("cedears & adrs conversion.xlsx", index_col=0)

    for ticker in conversiones.index:
        num, den = conversiones.loc[ticker, "RATIO"].split(":")
        conversiones.loc[ticker, "RATIO"] = int(num) / int(den)

    return conversiones




def get_market_dates(start_date, end_date):
    # Create a calendar
    nyse = mcal.get_calendar('NYSE')
    early = nyse.schedule(start_date=start_date, end_date=end_date)

    market_dates = list(mcal.date_range(early, frequency='1D'))
    market_dates = [x.replace(hour=0, minute=0, second=0, tzinfo=None) for x in market_dates]

    return market_dates





def group_stocks(movements):
    groups = {}
    for i in range(len(movements)):
        group, asset = movements.iloc[i][["GRUPO", "ACTIVO"]]
        if group not in groups: groups[group] = []
        if asset not in groups[group]: groups[group].append(asset)

    return groups





def get_quantities_df(movements, tickers, dates):
    cantidades = pd.DataFrame(index=dates, columns=tickers)

    cantidades.loc[:, :] = 0

    # cantidades["CASH"] = cantidades["CASH"].ffill()
    for i in range(len(movements)):
        datos = movements.iloc[i]
        fecha, operacion, ticker, cantidad, precio, importe = datos[
            ["FECHA", "OPERACION", "ACTIVO", "CANTIDAD", "PRECIO", "IMPORTE"]]

        if operacion == "compra":
            cantidades.loc[cantidades.index >= fecha, ticker] += cantidad
            cantidades.loc[cantidades.index >= fecha, "ARS"] -= importe
        elif operacion == "venta":
            cantidades.loc[cantidades.index >= fecha, ticker] -= cantidad
            cantidades.loc[cantidades.index >= fecha, "ARS"] += importe
        elif operacion == "fondeo":
            cantidades.loc[cantidades.index >= fecha, "ARS"] += importe
        elif operacion == "retiro":
            cantidades.loc[cantidades.index >= fecha, "ARS"] -= importe

    return cantidades




def get_prices_df(prices, tickers, groups, dates, ccl=None, conversions=None):
    if ccl is not None: ccl = ccl.copy(deep=True)
    if conversions is not None: conversions = conversions.copy(deep=True)
    precios = pd.DataFrame(index=dates, columns=tickers)

    # Completo el df de precios historicos
    for ticker in tickers:
        tc = 1
        factor = 1
        if ticker in groups["cedear"]:
            tc = ccl
            factor = conversions.loc[ticker, "RATIO"]
        precios[ticker] = prices[ticker]["Close"] * tc / factor
    precios.loc[:, "ARS"] = 1

    return precios


