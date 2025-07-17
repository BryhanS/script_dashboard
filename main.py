import streamlit as st
from modules import get_order_woocommerce
from modules import get_warehouse_name
from modules import get_warehouse_list
from modules import get_api_controlerp
from modules import get_sqlserver_engine
from modules import put_tracking_woocommerce

import datetime
import pandas as pd
import duckdb
from sqlalchemy.dialects.mssql import NVARCHAR


st.set_page_config(layout="wide", page_title="Dashboard Marketing", page_icon=":computer:")
st.session_state.theme = "dark"
st.title("Scripting")

if st.button("🧹 Limpiar caché global", key="clear_global_cache"):
    st.cache_data.clear()
    st.cache_resource.clear()

    st.session_state.clicked = False
    st.session_state.clicked_stock = False
    st.session_state.clicked_stock_accesorios = False
    st.session_state.clicked_transferencias = False
    st.session_state.clicked_woocommerce_descuento = False
    st.success("¡Caché global limpiado!")

st.divider() 

@st.cache_data(ttl=60)
def update_tracking_woocommerce(id,tracking_number):
    response = put_tracking_woocommerce(id, tracking_number)
    return response


uploaded_tracking = st.file_uploader("Sube csv tracking", type=["csv"], key="file_tracking_csv")
if uploaded_tracking is not None:
    df_uploaded_tracking = pd.read_csv(uploaded_tracking,encoding='utf-8')
    st.dataframe(df_uploaded_tracking, use_container_width=True, hide_index=True, key="uploaded_tracking")

    if st.button("tracking CSV"):
        try:
            for index, row in df_uploaded_tracking.iterrows():
                id = row['PEDIDO']
                tracking_number = row['TRACKING']
                response = update_tracking_woocommerce(id, tracking_number)
                if response:
                    st.success(response)
                else:
                    st.error(response)

        except Exception as e:
            st.error(f"Error al reemplazar la tabla: {e}")

st.divider() 

@st.cache_data(ttl=60)
def get_data_order():
    return get_order_woocommerce()



if 'clicked' not in st.session_state:
    st.session_state.clicked = False

def click_button():
    get_data_order.clear()
    st.session_state.clicked = True

    
st.text("El botón a continuación genera un reporte de las órdenes procesadas en Woocommerce.")
st.button('Order Woocommerce Reporte', on_click=click_button, key='order_woocommerce_button')
# Solo mostrar el DataFrame si se hizo clic en el botón


if st.session_state.clicked:
    df_json = get_data_order()

    if df_json is not None and not df_json.empty:
        st.dataframe(df_json, use_container_width=True, hide_index=True,key="order_dataframe")
    else:
        st.info("No hay datos para mostrar.")
st.divider()


#######
# script stock facturador



def warehouses_stock(array_warehouse):
    data_warehouse = get_warehouse_name()
    warehouses = data_warehouse
    stocks = []

    for warehouse in warehouses:
        found = False
        for one_warehouse in array_warehouse:
            if one_warehouse["warehouse_id"] == warehouse["warehouse_id"]:
                stocks.append(float(one_warehouse["stock"]))
                found = True 
                break
        if not found:
            stocks.append(float(0))
    return stocks

@st.cache_data
def convert_to_dataframe():
    data_final = get_api_controlerp()
    rows = []
    for items in data_final['data']['items']:
        if items['category'] == 'iPhone':
            ri = items['internal_id']
            split = ri.split("-")
            if len(split) >= 2:
                modelo = f'{split[0]}-{split[1]}-{split[2]}'
                modelo_grado = f'{split[0]}-{split[1]}-{split[2]}-{split[3]}'

            else:
                modelo = 'revisar'
            precio = float(items['sale_unit_price'])
            nuevo_precio = precio + 40
            princial, online, polo, taller, reparacion, transito_polo, taller_piezas, logistica_inversa, miraflores, miraflores_transito = warehouses_stock(items['warehouses'])
            rows.append([modelo,modelo_grado,ri,princial,online,polo, taller, reparacion, transito_polo,taller_piezas, logistica_inversa, miraflores, miraflores_transito])

    description_warehouse = get_warehouse_list()

    df = pd.DataFrame(rows, columns=["modelo", "modelo_grado", "sku"] + description_warehouse)
    df = pd.melt(df, id_vars=['modelo', 'modelo_grado','sku'], value_vars=description_warehouse,var_name='ubicacion',value_name='inventario')
    # df[df['inventario'] < 0]
    df_erp = df[df['inventario'] != 0]
    return df_erp

#######

if 'clicked_stock' not in st.session_state:
    st.session_state.clicked_stock = False

def click_stock_button():
    convert_to_dataframe.clear()
    st.session_state.clicked_stock = True


st.text("El botón a continuación genera un reporte de los stocks de productos en el sistema Facturador.")
st.button('Stock Facturador Reporte', on_click=click_stock_button, key='stock_facturador_button')
# Solo mostrar el DataFrame si se hizo clic en el botón
if st.session_state.clicked_stock:
    df_stock = convert_to_dataframe()
    if df_stock is not None and not df_stock.empty:
        st.dataframe(df_stock, use_container_width=True, hide_index=True,key="stock_dataframe")
    else:
        st.info("No hay datos para mostrar.")
st.divider()

########

@st.cache_data
def get_dataframe_accesorios():
    engine = get_sqlserver_engine()
    df = pd.read_sql_query("SELECT * FROM [dbo].[stock_temporal]", engine)
    return df
    

if 'clicked_stock_accesorios' not in st.session_state:
    st.session_state.clicked_stock_accesorios = False

def click_stock_accesorios_button():
    get_dataframe_accesorios.clear()
    st.session_state.clicked_stock_accesorios = True

st.text("El botón a continuación genera un reporte de los stocks de accesorios.")
st.button('Stock Accesorios Reporte', on_click=click_stock_accesorios_button, key='stock_accesorios_button')
# Solo mostrar el DataFrame si se hizo clic en el botón
if st.session_state.clicked_stock_accesorios:
    df_accesorios = get_dataframe_accesorios()
    if df_accesorios is not None and not df_accesorios.empty:
        st.dataframe(df_accesorios, use_container_width=True, hide_index=True,key="stock_accesorios_dataframe")
    else:
        st.info("No hay datos para mostrar.")
st.divider()

###########

@st.cache_data
def get_sql_transferencias():
    query_transferencias = f"""
        SELECT * FROM [dbo].[transferencia_almacenes]
        WHERE created_at BETWEEN '{date_init} 00:00:00' AND '{date_end} 23:59:59'
    """

    engine = get_sqlserver_engine()
    df = pd.read_sql_query(query_transferencias, engine)
    return df


cols = st.columns(3)
with cols[0]:
    date_init = st.date_input("Fecha Inicio", datetime.date.today())
with cols[1]:
    date_end = st.date_input("Fecha Fin", datetime.date.today())
with cols[2]:

    if 'clicked_transferencias' not in st.session_state:
        st.session_state.clicked_transferencias = False

    def click_transferencias():
        get_sql_transferencias.clear()
        st.session_state.clicked_transferencias = True

    st.button('Transferencia Facturador', on_click=click_transferencias, key='transferencias_button')


if st.session_state.clicked_transferencias:

    df_transferencias = get_sql_transferencias()
    if df_transferencias is not None and not df_transferencias.empty:
        st.dataframe(df_transferencias, use_container_width=True, hide_index=True,key="transferencias_dataframe")
    else:
        st.info("No hay datos para mostrar transferencias.")
st.divider()

### Equipos en Descuento Script
@st.cache_data(ttl=60)
def get_html_of_discounted_items():
    engine = get_sqlserver_engine()
    query_stock = """
        WITH filter_data as (
            SELECT [item_id] as sku
                ,([tienda_miraflores] + [tienda_caminos] + [tienda_online]) as cantidad
                ,[precio]
                FROM [dbo].[stock_temporal]
                WHERE ([tienda_miraflores] + [tienda_caminos] + [tienda_online]) > 0 AND [item_id] LIKE 'DESC-%')
        SELECT
            replace(sku, 'DESC-', '') as sku,
            cantidad,
            precio
            FROM filter_data;
    """
    query_woocommerce = """
            SELECT
             [SKU]
            ,[Nombre]
            ,[Valor(es) del atributo 1]
            ,[Valor(es) del atributo 2]
            ,[Valor(es) del atributo 3]
        FROM [dbo].[woocommerce_products]

    """

    df_stock_temporal = pd.read_sql_query(query_stock, engine)
    df_woocommerce = pd.read_sql_query(query_woocommerce, engine)
    
    df_html = duckdb.query("""
    SELECT 
        df_stock_temporal.sku,
        df_woocommerce.Nombre,
        df_woocommerce."Valor(es) del atributo 1",
        df_woocommerce."Valor(es) del atributo 2",
        df_woocommerce."Valor(es) del atributo 3",
        CAST(df_stock_temporal.precio AS INTEGER) as precio
        FROM df_stock_temporal
        LEFT JOIN df_woocommerce ON df_woocommerce.SKU = df_stock_temporal.sku
        ORDER BY df_stock_temporal.precio ASC , df_woocommerce.Nombre ASC
        """).to_df()
    
    html_data = []

    for _, row in df_html.iterrows():
        nombre = row['Nombre']
        valor_atributo_1 = row['Valor(es) del atributo 1']
        valor_atributo_2 = row['Valor(es) del atributo 2']
        valor_atributo_3 = row['Valor(es) del atributo 3']
        precio = row['precio'] + 40

        # Generar el HTML
        html_content = f"""
            <div
            class="elementor-element elementor-element-1607c76 e-flex e-con-boxed e-con e-parent e-lazyloaded"
            data-id="1607c76"
            data-element_type="container"  
            >
            <div class="e-con-inner">
                <div
                class="elementor-element elementor-element-6cc1a30 e-grid e-con-full e-con e-child"
                data-id="6cc1a30"
                data-element_type="container"
                >
                <div
                    class="elementor-element elementor-element-15ba5ad elementor-widget elementor-widget-text-editor"
                    data-id="15ba5ad"
                    data-element_type="widget"
                    data-widget_type="text-editor.default"
                >
                    <div class="elementor-widget-container">
                    <p><strong>{nombre} sin Face ID</strong></p>
                    </div>
                </div>
                <div
                    class="elementor-element elementor-element-fa99b10 elementor-widget elementor-widget-text-editor"
                    data-id="fa99b10"
                    data-element_type="widget"
                    data-widget_type="text-editor.default"
                >
                    <div class="elementor-widget-container">
                    <p style="text-align: center"><strong>{valor_atributo_1}</strong></p>
                    </div>
                </div>
                <div
                    class="elementor-element elementor-element-df0a806 elementor-widget elementor-widget-text-editor"
                    data-id="df0a806"
                    data-element_type="widget"
                    data-widget_type="text-editor.default"
                >
                    <div class="elementor-widget-container">
                    <p><strong>{valor_atributo_2}</strong></p>
                    </div>
                </div>
                <div
                    class="elementor-element elementor-element-e82dfd9 elementor-widget elementor-widget-text-editor"
                    data-id="e82dfd9"
                    data-element_type="widget"
                    data-widget_type="text-editor.default"
                >
                    <div class="elementor-widget-container">
                    <p><strong>{valor_atributo_3}</strong></p>
                    </div>
                </div>
                <div
                    class="elementor-element elementor-element-9f7e4f5 elementor-widget elementor-widget-text-editor"
                    data-id="9f7e4f5"
                    data-element_type="widget"
                    data-widget_type="text-editor.default"
                >
                    <div class="elementor-widget-container">
                    <p style="text-align: center">
                        <span style="color: #009bdb; font-size: 14pt"
                        ><strong>S/ {precio}</strong></span
                        >
                    </p>
                    </div>
                </div>
                </div>
            </div>
            </div>
        """
        # file.write(html_content + '\n')
        html_data.append(html_content)



    return html_data



if 'clicked_woocommerce_descuento' not in st.session_state:
    st.session_state.clicked_woocommerce_descuento = False

def click_woocommerce_descuento():
    get_dataframe_accesorios.clear()
    st.session_state.clicked_woocommerce_descuento = True

st.text("El botón a continuación genera un equipos en descuento.")
st.button('Descuento Woocommerce', on_click=click_woocommerce_descuento, key='woocommerce_descuento_button')
# Solo mostrar el DataFrame si se hizo clic en el botón

if st.session_state.clicked_woocommerce_descuento:
    df_html = get_html_of_discounted_items()


    if df_html is not None and len(df_html)>0 :
        st.code('\n'.join(df_html), language='html')

    else:
        st.info("No hay datos para mostrar.")
st.divider()


uploaded_file = st.file_uploader("Sube csv woocommerce", type=["csv"], key="file_woocommerce_csv")
if uploaded_file is not None:
    df_uploaded = pd.read_csv(uploaded_file,encoding='utf-8')
    st.dataframe(df_uploaded, use_container_width=True, hide_index=True, key="uploaded_dataframe")

    if st.button("Procesar CSV"):
        engine = get_sqlserver_engine()
        try:
            df_uploaded.to_sql('woocommerce_products', con=engine, if_exists='replace', index=False, dtype={'Valor(es) del atributo 2': NVARCHAR(255)})
            st.success("Tabla 'woocommerce_products' reemplazada exitosamente.")
        except Exception as e:
            st.error(f"Error al reemplazar la tabla: {e}")
   