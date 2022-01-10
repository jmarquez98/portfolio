import pandas as pd
import pandas_market_calendars as mcal
import yfinance as yf
from datetime import datetime


movs = pd.read_excel("movimientos.xlsx")

first_date = movs.loc[0, "FECHA"]
hoy = datetime.now().replace(hour=0, minute=0, second=0)

# Create a calendar
nyse = mcal.get_calendar('NYSE')
early = nyse.schedule(start_date=first_date, end_date=hoy)

market_dates = list(mcal.date_range(early, frequency='1D'))
market_dates = [x.replace(hour=0, minute=0, second=0, tzinfo=None) for x in market_dates]
movs_dates = list(set(movs["FECHA"]))


dates = list(set(market_dates + movs_dates))
dates = sorted(dates)

#print(dates)


stocks = movs.loc[movs.TIPO=="stock"]
tickers = list(set(stocks.TICKER.to_list()))

prices = yf.download(tickers, group_by="ticker")

data = {}
for ticker in tickers:
    data[ticker] = prices[ticker]




market_df = pd.DataFrame(index=dates, columns=tickers+["ARS"])
cantidades, precios, importes = market_df.copy(deep=True), market_df.copy(deep=True), market_df.copy(deep=True)


for ticker in tickers:
    precios[ticker] = data[ticker]["Close"]
precios.loc[:, "ARS"] = 1


operaciones = movs.loc[(movs.OPERACION=="compra") | (movs.OPERACION=="venta")]
operaciones = operaciones.groupby("FECHA")[["TICKER", "OPERACION", "CANTIDAD", "PRECIO"]]\
    .apply(lambda x: x.set_index('TICKER').to_dict(orient='index'))\
    .to_dict()


cantidades.loc[:, :] = 0


#cantidades["CASH"] = cantidades["CASH"].ffill()
for i in range(len(movs)):
    datos = movs.iloc[i]
    fecha, operacion, ticker, cantidad, precio, importe = datos[["FECHA", "OPERACION", "TICKER", "CANTIDAD", "PRECIO", "IMPORTE"]]

    if operacion=="compra":
        cantidades.loc[cantidades.index >= fecha, ticker] += cantidad
        cantidades.loc[cantidades.index >= fecha, "ARS"] -= importe
    elif operacion == "venta":
        cantidades.loc[cantidades.index >= fecha, ticker] -= cantidad
        cantidades.loc[cantidades.index >= fecha, "ARS"] += importe
    elif operacion=="fondeo":
        cantidades.loc[cantidades.index >= fecha, "ARS"] += importe
    elif operacion == "retiro":
        cantidades.loc[cantidades.index >= fecha, "ARS"] -= importe

importes = cantidades * precios
composicion = importes.div(importes.sum(axis=1), axis=0)
retornos = precios.pct_change()
retornos_port = composicion * retornos

cantidades.to_excel("cantidades.xlsx")
precios.to_excel("precios.xlsx")
importes.to_excel("importes.xlsx")
composicion.to_excel("composicion.xlsx")
retornos.to_excel("retornos.xlsx")
retornos_port.to_excel("retornos_port.xlsx")