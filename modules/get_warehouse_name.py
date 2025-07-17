import json
import os


base_dir = os.path.dirname(__file__)  # Directorio actual del módulo
file_path = os.path.join(base_dir, '../data/warehouses.json')  # Ruta al archivo JSON

def get_warehouse_name():
    with open(file_path, 'r') as file:
        data = json.load(file)
        return data
    

def get_warehouse_list():
    description_warehouse = ["almacen_principal", "tienda_online", "tienda_caminos", "almacen_taller", "almacen_reparacion", "almacen_transito_caminos", "almacen_taller_piezas", "almacen_inversa", "tienda_miraflores","almacen_transito_miraflores"]
    return description_warehouse

# get_warehouse_name()
# get_warehouse_list()