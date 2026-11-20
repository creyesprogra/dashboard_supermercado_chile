import matplotlib.pyplot as plt
import pandas as pd
import streamlit as st

st.set_page_config(page_title="Precios en Supermercados de Chile", layout="wide")


def cargar_datos(ruta_csv):
  df = pd.read_csv(ruta_csv)
  df["Brecha_precio"] = df["Precio maximo"] - df["Precio minimo"]
  return df


def filtrar_datos(df, region, grupos, rango_precio):
  datos = df.copy()
  if region != "Todas":
    datos = datos[datos["Region"] == region]
  if grupos:
    datos = datos[datos["Grupo"].isin(grupos)]
  datos = datos[
      (datos["Precio promedio"] >= rango_precio[0])
      & (datos["Precio promedio"] <= rango_precio[1])
  ]
  return datos


def calcular_indicadores(datos):
  if datos.empty:
    return 0.0, 0.0
  precio_prom = datos["Precio promedio"].mean()
  brecha_prom = datos["Brecha_precio"].mean()
  return precio_prom, brecha_prom


def crear_grafico_barras(datos):
  promedios_grupo = (
      datos.groupby("Grupo")["Precio promedio"]
      .mean()
      .sort_values(ascending=False)
  )
  plt.figure(figsize=(8, 4))
  plt.bar(
      promedios_grupo.index,
      promedios_grupo.values,
      label="Precio promedio ($ CLP)",
  )
  plt.title("Precio promedio por grupo de producto")
  plt.xlabel("Grupo de producto")
  plt.ylabel("Precio promedio ($ CLP)")
  plt.xticks(rotation=25)
  plt.legend()
  plt.tight_layout()
  return plt


def crear_grafico_lineas(datos):
  promedios_mes = datos.groupby("Mes")["Precio promedio"].mean().sort_index()
  plt.figure(figsize=(8, 4))
  plt.plot(
      promedios_mes.index,
      promedios_mes.values,
      marker="o",
      label="Precio promedio mensual ($ CLP)",
  )
  plt.title("Evolución mensual del precio promedio")
  plt.xlabel("Mes")
  plt.ylabel("Precio promedio ($ CLP)")
  plt.xticks(promedios_mes.index)
  plt.legend()
  plt.tight_layout()
  return plt


def crear_grafico_dispersion(datos):
  plt.figure(figsize=(8, 4))
  plt.scatter(
      datos["Precio minimo"],
      datos["Precio promedio"],
      alpha=0.5,
      label="Registros filtrados",
  )
  plt.title("Relación entre precio mínimo y precio promedio")
  plt.xlabel("Precio mínimo ($ CLP)")
  plt.ylabel("Precio promedio ($ CLP)")
  plt.legend()
  plt.tight_layout()
  return plt


def main():
  st.title("Monitor de Precios en Supermercados de Chile")
  st.markdown(
      "Aplicación interactiva para analizar precios registrados en **supermercados** "
      "a partir de **ODEPA — Precios al Consumidor** "
      "([Enlace a la fuente ODEPA](https://datos.odepa.gob.cl/dataset/precios-consumidor))."
  )

  with st.expander("Instrucciones de uso"):
    st.write(
        "1. En la barra lateral, elige una **Región**, selecciona uno o más **Grupos** "
        "y ajusta el **Rango de precio promedio ($ CLP)**.\n"
        "2. Revisa los indicadores, los tres gráficos y la tabla, que cambian según tus filtros."
    )

  df = cargar_datos("datos_supermercado_limpio.csv.csv")

  st.sidebar.header("Filtros interactivos")
  regiones = ["Todas"] + sorted(df["Region"].dropna().unique().tolist())
  region_sel = st.sidebar.selectbox("Selecciona una región", regiones)

  grupos_disp = sorted(df["Grupo"].dropna().unique().tolist())
  grupos_sel = st.sidebar.multiselect(
      "Selecciona grupos de productos", grupos_disp
  )

  precio_min = float(df["Precio promedio"].min())
  precio_max = float(df["Precio promedio"].max())
  rango_precio = st.sidebar.slider(
      "Rango de precio promedio ($ CLP)",
      min_value=precio_min,
      max_value=precio_max,
      value=(precio_min, precio_max),
  )

  datos_filtrados = filtrar_datos(df, region_sel, grupos_sel, rango_precio)

  st.subheader("Indicadores principales")
  precio_prom, brecha_prom = calcular_indicadores(datos_filtrados)
  col1, col2, col3 = st.columns(3)
  col1.metric("Precio promedio ($ CLP)", f"${precio_prom:,.0f}")
  col2.metric("Brecha prom. máx. - mín. ($ CLP)", f"${brecha_prom:,.0f}")
  col3.metric("Registros mostrados", f"{len(datos_filtrados):,}")

  if datos_filtrados.empty:
    st.warning("No hay datos para esa combinación de filtros.")
    return

  st.subheader("Gráficos")
  g1, g2 = st.columns(2)
  with g1:
    st.pyplot(crear_grafico_barras(datos_filtrados))
  with g2:
    st.pyplot(crear_grafico_lineas(datos_filtrados))

  st.pyplot(crear_grafico_dispersion(datos_filtrados))

  st.subheader("Tabla de datos filtrados")
  columnas_tabla = [
      "Anio",
      "Mes",
      "Region",
      "Sector",
      "Grupo",
      "Producto",
      "Unidad",
      "Precio minimo",
      "Precio maximo",
      "Precio promedio",
  ]
  st.dataframe(datos_filtrados[columnas_tabla], use_container_width=True)


if __name__ == "__main__":
  main()
