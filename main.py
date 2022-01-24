import pandas as pd
import pandas_market_calendars as mcal
import yfinance as yf
from datetime import datetime
import sys
import pathlib
path = str(pathlib.Path(__file__).parent.absolute())

import utils as ut







# Obtengo excel con movimientos de cartera
movs = pd.read_excel("movimientos.xlsx")
movs = movs.loc[movs.GRUPO!="fci"]

conversiones = ut.get_cedears_conversion()

# Obtengo fechas de mercado y de movimientos
start_date = movs.loc[0, "FECHA"]
hoy = datetime.now().replace(hour=0, minute=0, second=0)
market_dates = ut.get_market_dates(start_date=start_date, end_date=hoy)

movs_dates = list(set(movs["FECHA"]))
dates = list(set(market_dates + movs_dates))
dates = sorted(dates)





# Obtengo precios historicos de equities y bonos
data, tickers, fallas_t = ut.get_historical_prices(movements=movs)


ccl = data["GGAL.BA"]["Close"] * 10 / data["GGAL"]["Close"]
ccl.ffill(inplace=True)

mep = data["GD30"]["Close"] / data["GD30D"]["Close"]
mep.ffill(inplace=True)




# Agrupo tickers segun tipo de activo en un diccionario
grupos = ut.group_stocks(movements=movs)



# Obtengo df cuyas filas son fechas de mercado y cada columna corresponde a los precios historicos de cada activo
precios = ut.get_prices_df(prices=data, tickers=tickers, groups=grupos, dates=dates, mep=mep, ccl=ccl, conversions=conversiones)


operaciones = movs.loc[(movs.OPERACION=="compra") | (movs.OPERACION=="venta")]
operaciones = operaciones.groupby("FECHA")[["ACTIVO", "OPERACION", "CANTIDAD", "PRECIO"]]\
    .apply(lambda x: x.set_index('ACTIVO').to_dict(orient='index'))\
    .to_dict()


# Obtengo df que contiene para cada fecha la cantidad que se tiene de cada activo
cantidades = ut.get_quantities_df(movements=movs, dates=dates, tickers=tickers+["ARS", "USD MEP"])

# Obtengo df que contiene para cada fecha el importe que se tiene de cada activo (precio * cantidad)
importes = cantidades * precios

# Obtengo df con la ponderacion que cada papel tiene en cartera para cada fecha
composicion = importes.div(importes.sum(axis=1), axis=0)

# Obtengo df con los retornos historicos de cada activo para cada fecha
retornos = precios.pct_change()

# Obtengo df con los retornos historicos de cada activo para cada fecha, podnerados por su peso dentro del portfolio
retornos_port = composicion * retornos







cantidades.to_excel("cantidades.xlsx")
precios.to_excel("precios.xlsx")
importes.to_excel("importes.xlsx")
composicion.to_excel("composicion.xlsx")
retornos.to_excel("retornos.xlsx")
retornos_port.to_excel("retornos_port.xlsx")