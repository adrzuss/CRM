from flask import Blueprint, render_template, request, redirect, flash, url_for, jsonify, current_app, session
from flask import g
from werkzeug.utils import secure_filename
import os
from models.articulos import Articulo, Marca, Stock, Precio, ListasPrecios, Rubro, ArticuloCompuesto, ProvByArt, PedirEnVentas, Colores, ArticulosColores, DetallesArticulos, ArticulosDetalles
from models.configs import AlcIva, TipoArticulos, TipoBalances, AlcIB
from models.sucursales import Sucursales
from models.proveedores import Proveedores
from services.articulos import get_listado_precios, obtener_stock_sucursales, update_insert_articulo_compuesto, \
                               eliminarComp, obtenerArticulosMarcaRubro, procesar_nuevo_balance, \
                               procesar_cambio_precio, procesar_remito_a_sucursal, get_listado_articulos, \
                               get_listado_stock, get_listado_stock_faltantes, enviar_remito_sucursal, recibir_remito_sucursal, \
                               get_remitos_sucursales, get_detalle_remito, guardar_articulo, get_detalle_articulo, \
                               get_detalle_full_articulo    
from sqlalchemy import func, and_, or_
from sqlalchemy.sql import text
from utils.db import db
from utils.config import allowed_file
from utils.utils import check_session, convertir_decimal
from utils.msg_alertas import alertas_mensajes
from datetime import datetime, date
from decimal import Decimal

bp_reportes = Blueprint('reportes', __name__, template_folder='../templates/reportes')


@bp_reportes.route('/reporte_gerencial')
@check_session
@alertas_mensajes
def reporte_gerencial():
    return render_template('reporte-gerencial.html')