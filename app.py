#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Sistema de Gestión de Fábrica - APK Android
Flask + SQLite + FPDF2
Diseño optimizado para modo horizontal (Landscape)
"""

import os
import io
from datetime import datetime
from flask import Flask, render_template, request, jsonify, send_file
from models import db, Producto, Produccion, Venta, Gasto, calcular_costo_unitario_mes, calcular_dinero_total, calcular_totales_mes, get_producciones_con_stock, get_dashboard_stats
from fpdf import FPDF

# Configuración de rutas para portabilidad
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
TEMPLATE_DIR = os.path.join(BASE_DIR, 'templates')
STATIC_DIR = os.path.join(BASE_DIR, 'static')
DATABASE_DIR = os.path.join(BASE_DIR, 'database')

# Asegurar directorios
os.makedirs(DATABASE_DIR, exist_ok=True)

app = Flask(__name__, template_folder=TEMPLATE_DIR, static_folder=STATIC_DIR)
app.config['SECRET_KEY'] = 'factory-app-secret-2024'
app.config['SQLALCHEMY_DATABASE_URI'] = f'sqlite:///{os.path.join(DATABASE_DIR, "fabrica.db")}'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db.init_app(app)


# ============================================================================
# UTILIDADES
# ============================================================================

def format_guaranies(valor):
    """Formatea número como moneda en guaraníes: Gs. 1.500.000"""
    if valor is None:
        valor = 0
    return f"Gs. {valor:,.0f}".replace(",", ".")


def get_mes_nombre(mes_num):
    """Devuelve el nombre del mes en español"""
    meses = ['', 'Enero', 'Febrero', 'Marzo', 'Abril', 'Mayo', 'Junio',
             'Julio', 'Agosto', 'Septiembre', 'Octubre', 'Noviembre', 'Diciembre']
    return meses[mes_num] if 1 <= mes_num <= 12 else ''


# ============================================================================
# RUTAS PRINCIPALES
# ============================================================================

@app.route('/')
def index():
    """Página principal - SPA"""
    return render_template('index.html')


# ============================================================================
# API - DASHBOARD
# ============================================================================

@app.route('/api/dashboard')
def api_dashboard():
    """API para estadísticas del dashboard"""
    stats = get_dashboard_stats()
    
    # Productos con bajo stock
    productos_bajo_stock = Producto.query.filter(
        Producto.stock_actual < 10,
        Producto.activo == True
    ).all()
    
    # Últimas ventas
    ultimas_ventas = Venta.query.order_by(Venta.fecha.desc()).limit(5).all()
    
    # Últimos gastos
    ultimos_gastos = Gasto.query.order_by(Gasto.fecha.desc()).limit(5).all()
    
    return jsonify({
        'stats': stats,
        'productos_bajo_stock': [p.to_dict() for p in productos_bajo_stock],
        'ultimas_ventas': [v.to_dict() for v in ultimas_ventas],
        'ultimos_gastos': [g.to_dict() for g in ultimos_gastos]
    })


# ============================================================================
# API - PRODUCTOS
# ============================================================================

@app.route('/api/productos', methods=['GET'])
def api_productos_list():
    """Listar todos los productos activos"""
    productos = Producto.query.filter_by(activo=True).order_by(Producto.nombre).all()
    return jsonify([p.to_dict() for p in productos])


@app.route('/api/productos', methods=['POST'])
def api_producto_create():
    """Crear nuevo producto"""
    data = request.get_json()
    
    producto = Producto(
        nombre=data.get('nombre'),
        stock_actual=data.get('stock_inicial', 0),
        precio_mayorista=data.get('precio_mayorista', 0),
        precio_minorista=data.get('precio_minorista', 0)
    )
    
    db.session.add(producto)
    db.session.commit()
    
    return jsonify({'success': True, 'producto': producto.to_dict()})


@app.route('/api/productos/<int:id>', methods=['PUT'])
def api_producto_update(id):
    """Actualizar producto"""
    producto = Producto.query.get_or_404(id)
    data = request.get_json()
    
    producto.nombre = data.get('nombre', producto.nombre)
    producto.precio_mayorista = data.get('precio_mayorista', producto.precio_mayorista)
    producto.precio_minorista = data.get('precio_minorista', producto.precio_minorista)
    
    db.session.commit()
    
    return jsonify({'success': True, 'producto': producto.to_dict()})


@app.route('/api/productos/<int:id>', methods=['DELETE'])
def api_producto_delete(id):
    """Eliminar producto (soft delete)"""
    producto = Producto.query.get_or_404(id)
    
    # Verificar si tiene producciones o ventas
    if producto.producciones or producto.ventas:
        return jsonify({
            'success': False,
            'error': 'No se puede eliminar: tiene producciones o ventas asociadas'
        }), 400
    
    producto.activo = False
    db.session.commit()
    
    return jsonify({'success': True})


# ============================================================================
# API - PRODUCCIÓN
# ============================================================================

@app.route('/api/produccion', methods=['GET'])
def api_produccion_list():
    """Listar producción"""
    produccion = Produccion.query.order_by(
        Produccion.anio.desc(),
        Produccion.mes.desc()
    ).all()
    return jsonify([p.to_dict() for p in produccion])


@app.route('/api/produccion', methods=['POST'])
def api_produccion_create():
    """Crear nueva producción"""
    data = request.get_json()
    
    mes = data.get('mes')
    anio = data.get('anio')
    
    # Calcular costo unitario para este mes
    costo_unitario = calcular_costo_unitario_mes(mes, anio)
    
    produccion = Produccion(
        producto_id=data.get('producto_id'),
        cantidad=data.get('cantidad'),
        mes=mes,
        anio=anio,
        costo_unitario_calculado=costo_unitario
    )
    
    db.session.add(produccion)
    
    # Actualizar stock del producto
    producto = Producto.query.get(data.get('producto_id'))
    producto.stock_actual += data.get('cantidad')
    
    db.session.commit()
    
    return jsonify({
        'success': True,
        'produccion': produccion.to_dict(),
        'costo_unitario': costo_unitario
    })


@app.route('/api/produccion/<int:id>', methods=['DELETE'])
def api_produccion_delete(id):
    """Eliminar producción"""
    produccion = Produccion.query.get_or_404(id)
    
    # Verificar si tiene ventas asociadas
    if produccion.ventas:
        return jsonify({
            'success': False,
            'error': 'No se puede eliminar: tiene ventas asociadas'
        }), 400
    
    # Restar del stock
    producto = Producto.query.get(produccion.producto_id)
    producto.stock_actual -= produccion.cantidad
    
    db.session.delete(produccion)
    db.session.commit()
    
    return jsonify({'success': True})


@app.route('/api/productos/<int:producto_id>/producciones-disponibles')
def api_producciones_disponibles(producto_id):
    """Obtener producciones con stock disponible para un producto"""
    producciones = get_producciones_con_stock(producto_id)
    return jsonify(producciones)


# ============================================================================
# API - VENTAS
# ============================================================================

@app.route('/api/ventas', methods=['GET'])
def api_ventas_list():
    """Listar ventas"""
    ventas = Venta.query.order_by(Venta.fecha.desc()).all()
    return jsonify([v.to_dict() for v in ventas])


@app.route('/api/ventas', methods=['POST'])
def api_venta_create():
    """Crear nueva venta"""
    data = request.get_json()
    
    producto_id = data.get('producto_id')
    produccion_id = data.get('produccion_id')
    cantidad = data.get('cantidad')
    tipo_precio = data.get('tipo_precio')
    descuento = data.get('descuento', 0)
    
    # Obtener producto y producción
    producto = Producto.query.get_or_404(producto_id)
    produccion = Produccion.query.get_or_404(produccion_id)
    
    # Verificar stock disponible
    vendido = db.session.query(func.sum(Venta.cantidad)).filter_by(
        produccion_id=produccion_id
    ).scalar() or 0
    
    disponible = produccion.cantidad - vendido
    
    if cantidad > disponible:
        return jsonify({
            'success': False,
            'error': f'Stock insuficiente. Solo hay {disponible} unidades disponibles'
        }), 400
    
    if cantidad > producto.stock_actual:
        return jsonify({
            'success': False,
            'error': 'Stock insuficiente en el producto'
        }), 400
    
    # Determinar precio aplicado
    if tipo_precio == 'mayorista':
        precio_aplicado = producto.precio_mayorista
    else:
        precio_aplicado = producto.precio_minorista
    
    # Calcular ganancia real
    costo_total = produccion.costo_unitario_calculado * cantidad
    ingreso_total = (precio_aplicado * cantidad) - descuento
    ganancia_real = ingreso_total - costo_total
    
    # Crear venta
    mes_actual = datetime.now().month
    anio_actual = datetime.now().year
    
    venta = Venta(
        producto_id=producto_id,
        produccion_id=produccion_id,
        cantidad=cantidad,
        precio_aplicado=precio_aplicado,
        descuento=descuento,
        mes_venta=mes_actual,
        anio_venta=anio_actual,
        ganancia_real=ganancia_real
    )
    
    db.session.add(venta)
    
    # Actualizar stock
    producto.stock_actual -= cantidad
    
    db.session.commit()
    
    return jsonify({
        'success': True,
        'venta': venta.to_dict(),
        'ganancia_real': ganancia_real
    })


@app.route('/api/ventas/<int:id>', methods=['DELETE'])
def api_venta_delete(id):
    """Eliminar venta"""
    venta = Venta.query.get_or_404(id)
    
    # Devolver stock al producto
    producto = Producto.query.get(venta.producto_id)
    producto.stock_actual += venta.cantidad
    
    db.session.delete(venta)
    db.session.commit()
    
    return jsonify({'success': True})


# ============================================================================
# API - GASTOS
# ============================================================================

@app.route('/api/gastos', methods=['GET'])
def api_gastos_list():
    """Listar gastos"""
    gastos = Gasto.query.order_by(Gasto.fecha.desc()).all()
    return jsonify([g.to_dict() for g in gastos])


@app.route('/api/gastos', methods=['POST'])
def api_gasto_create():
    """Crear nuevo gasto"""
    data = request.get_json()
    
    gasto = Gasto(
        concepto=data.get('concepto'),
        monto=data.get('monto'),
        tipo=data.get('tipo'),
        mes_gasto=data.get('mes'),
        anio_gasto=data.get('anio')
    )
    
    db.session.add(gasto)
    db.session.commit()
    
    return jsonify({'success': True, 'gasto': gasto.to_dict()})


@app.route('/api/gastos/<int:id>', methods=['DELETE'])
def api_gasto_delete(id):
    """Eliminar gasto"""
    gasto = Gasto.query.get_or_404(id)
    db.session.delete(gasto)
    db.session.commit()
    
    return jsonify({'success': True})


@app.route('/api/gastos/totales')
def api_gastos_totales():
    """Obtener totales de gastos por tipo"""
    total_fabrica = db.session.query(func.sum(Gasto.monto)).filter_by(tipo='Fabrica').scalar() or 0
    total_personal = db.session.query(func.sum(Gasto.monto)).filter_by(tipo='Personal').scalar() or 0
    
    return jsonify({
        'fabrica': total_fabrica,
        'personal': total_personal,
        'total': total_fabrica + total_personal
    })


# ============================================================================
# API - REPORTES Y PDF
# ============================================================================

@app.route('/api/reportes/datos')
def api_reportes_datos():
    """Obtener datos para reportes"""
    mes = request.args.get('mes', type=int)
    anio = request.args.get('anio', type=int)
    
    # Query base
    ventas_query = Venta.query
    gastos_query = Gasto.query
    
    if mes:
        ventas_query = ventas_query.filter_by(mes_venta=mes)
        gastos_query = gastos_query.filter_by(mes_gasto=mes)
    
    if anio:
        ventas_query = ventas_query.filter_by(anio_venta=anio)
        gastos_query = gastos_query.filter_by(anio_gasto=anio)
    
    ventas = ventas_query.order_by(Venta.fecha.desc()).all()
    gastos = gastos_query.order_by(Gasto.fecha.desc()).all()
    
    # Calcular totales
    totales = calcular_totales_mes(mes or datetime.now().month, anio or datetime.now().year)
    
    return jsonify({
        'ventas': [v.to_dict() for v in ventas],
        'gastos': [g.to_dict() for g in gastos],
        'totales': totales,
        'mes': mes,
        'anio': anio
    })


@app.route('/api/reportes/pdf')
def api_generar_pdf():
    """Generar reporte PDF usando FPDF2"""
    mes = request.args.get('mes', type=int)
    anio = request.args.get('anio', type=int)
    
    # Crear PDF en memoria
    pdf = FPDF(orientation='L', unit='mm', format='A4')  # Landscape
    pdf.add_page()
    pdf.set_auto_page_break(auto=True, margin=10)
    
    # Usar fuente estándar (Helvetica/Arial)
    font_family = 'Helvetica'
    
    # Título
    pdf.set_font(font_family, 'B', 20)
    pdf.cell(0, 12, 'Reporte de Fábrica', ln=True, align='C')
    
    # Subtítulo
    pdf.set_font(font_family, '', 14)
    if mes and anio:
        pdf.cell(0, 8, f'{get_mes_nombre(mes)} {anio}', ln=True, align='C')
    elif anio:
        pdf.cell(0, 8, f'Año {anio}', ln=True, align='C')
    else:
        pdf.cell(0, 8, 'Reporte General', ln=True, align='C')
    
    pdf.ln(5)
    
    # Fecha de generación
    pdf.set_font(font_family, '', 10)
    pdf.cell(0, 6, f'Generado: {datetime.now().strftime("%d/%m/%Y %H:%M")}', align='R')
    pdf.ln(10)
    
    # Calcular totales
    ventas_query = db.session.query(func.sum(
        Venta.precio_aplicado * Venta.cantidad - Venta.descuento
    ))
    gastos_fabrica_query = db.session.query(func.sum(Gasto.monto)).filter(Gasto.tipo == 'Fabrica')
    gastos_personal_query = db.session.query(func.sum(Gasto.monto)).filter(Gasto.tipo == 'Personal')
    ganancias_query = db.session.query(func.sum(Venta.ganancia_real))
    
    if mes and anio:
        ventas_query = ventas_query.filter(Venta.mes_venta == mes, Venta.anio_venta == anio)
        gastos_fabrica_query = gastos_fabrica_query.filter(Gasto.mes_gasto == mes, Gasto.anio_gasto == anio)
        gastos_personal_query = gastos_personal_query.filter(Gasto.mes_gasto == mes, Gasto.anio_gasto == anio)
        ganancias_query = ganancias_query.filter(Venta.mes_venta == mes, Venta.anio_venta == anio)
    elif anio:
        ventas_query = ventas_query.filter(Venta.anio_venta == anio)
        gastos_fabrica_query = gastos_fabrica_query.filter(Gasto.anio_gasto == anio)
        gastos_personal_query = gastos_personal_query.filter(Gasto.anio_gasto == anio)
        ganancias_query = ganancias_query.filter(Venta.anio_venta == anio)
    
    total_ventas = ventas_query.scalar() or 0
    total_gastos_fabrica = gastos_fabrica_query.scalar() or 0
    total_gastos_personal = gastos_personal_query.scalar() or 0
    total_gastos = total_gastos_fabrica + total_gastos_personal
    total_ganancias = ganancias_query.scalar() or 0
    
    # SECCIÓN: RESUMEN FINANCIERO
    pdf.set_font(font_family, 'B', 14)
    pdf.set_fill_color(50, 50, 50)
    pdf.set_text_color(255, 255, 255)
    pdf.cell(0, 10, 'Resumen Financiero', ln=True, fill=True)
    pdf.set_text_color(0, 0, 0)
    pdf.ln(3)
    
    pdf.set_font(font_family, '', 11)
    datos_resumen = [
        ('Total Ventas:', format_guaranies(total_ventas)),
        ('Gastos de Fabrica:', format_guaranies(total_gastos_fabrica)),
        ('Gastos Personales:', format_guaranies(total_gastos_personal)),
        ('Total Gastos:', format_guaranies(total_gastos)),
        ('Ganancia Neta:', format_guaranies(total_ganancias)),
    ]
    
    for label, valor in datos_resumen:
        pdf.set_font(font_family, 'B', 11)
        pdf.cell(60, 7, label, ln=0)
        pdf.set_font(font_family, '', 11)
        pdf.cell(0, 7, valor, ln=1)
    
    pdf.ln(5)
    
    # SECCIÓN: VENTAS DETALLADAS
    pdf.set_font(font_family, 'B', 14)
    pdf.set_fill_color(50, 50, 50)
    pdf.set_text_color(255, 255, 255)
    pdf.cell(0, 10, 'Detalle de Ventas', ln=True, fill=True)
    pdf.set_text_color(0, 0, 0)
    pdf.ln(3)
    
    ventas_query = Venta.query
    if mes and anio:
        ventas_query = ventas_query.filter(Venta.mes_venta == mes, Venta.anio_venta == anio)
    elif anio:
        ventas_query = ventas_query.filter(Venta.anio_venta == anio)
    ventas = ventas_query.order_by(Venta.fecha.desc()).limit(50).all()
    
    if ventas:
        # Encabezados
        pdf.set_font(font_family, 'B', 10)
        pdf.set_fill_color(220, 220, 220)
        pdf.cell(30, 7, 'Fecha', fill=True)
        pdf.cell(60, 7, 'Producto', fill=True)
        pdf.cell(25, 7, 'Cant.', align='C', fill=True)
        pdf.cell(35, 7, 'Precio', align='R', fill=True)
        pdf.cell(35, 7, 'Desc.', align='R', fill=True)
        pdf.cell(35, 7, 'Total', align='R', fill=True)
        pdf.cell(35, 7, 'Ganancia', align='R', fill=True)
        pdf.ln()
        
        # Datos
        pdf.set_font(font_family, '', 9)
        for venta in ventas:
            pdf.cell(30, 6, venta.fecha.strftime('%d/%m/%Y'))
            pdf.cell(60, 6, venta.producto.nombre[:30])
            pdf.cell(25, 6, str(venta.cantidad), align='C')
            pdf.cell(35, 6, format_guaranies(venta.precio_aplicado), align='R')
            pdf.cell(35, 6, format_guaranies(venta.descuento), align='R')
            total = (venta.precio_aplicado * venta.cantidad) - venta.descuento
            pdf.cell(35, 6, format_guaranies(total), align='R')
            pdf.cell(35, 6, format_guaranies(venta.ganancia_real), align='R')
            pdf.ln()
        
        # Total
        pdf.set_font(font_family, 'B', 10)
        pdf.cell(150, 7, 'Total Ventas:', align='R')
        pdf.cell(0, 7, format_guaranies(total_ventas), align='R')
        pdf.ln()
    else:
        pdf.set_font(font_family, '', 11)
        pdf.cell(0, 7, 'No hay ventas registradas', ln=True)
    
    pdf.ln(5)
    
    # Nueva página para gastos si es necesario
    if pdf.get_y() > 150:
        pdf.add_page()
    
    # SECCIÓN: GASTOS DETALLADOS
    pdf.set_font(font_family, 'B', 14)
    pdf.set_fill_color(50, 50, 50)
    pdf.set_text_color(255, 255, 255)
    pdf.cell(0, 10, 'Detalle de Gastos', ln=True, fill=True)
    pdf.set_text_color(0, 0, 0)
    pdf.ln(3)
    
    gastos_query = Gasto.query
    if mes and anio:
        gastos_query = gastos_query.filter(Gasto.mes_gasto == mes, Gasto.anio_gasto == anio)
    elif anio:
        gastos_query = gastos_query.filter(Gasto.anio_gasto == anio)
    gastos = gastos_query.order_by(Gasto.fecha.desc()).limit(50).all()
    
    if gastos:
        # Encabezados
        pdf.set_font(font_family, 'B', 10)
        pdf.set_fill_color(220, 220, 220)
        pdf.cell(30, 7, 'Fecha', fill=True)
        pdf.cell(80, 7, 'Concepto', fill=True)
        pdf.cell(30, 7, 'Tipo', align='C', fill=True)
        pdf.cell(40, 7, 'Monto', align='R', fill=True)
        pdf.ln()
        
        # Datos
        pdf.set_font(font_family, '', 9)
        for gasto in gastos:
            pdf.cell(30, 6, gasto.fecha.strftime('%d/%m/%Y'))
            pdf.cell(80, 6, gasto.concepto[:40])
            pdf.cell(30, 6, gasto.tipo, align='C')
            pdf.cell(40, 6, format_guaranies(gasto.monto), align='R')
            pdf.ln()
        
        # Totales
        pdf.ln(3)
        pdf.set_font(font_family, 'B', 10)
        pdf.cell(140, 7, 'Total Gastos de Fabrica:', align='R')
        pdf.cell(0, 7, format_guaranies(total_gastos_fabrica), align='R')
        pdf.ln()
        pdf.cell(140, 7, 'Total Gastos Personales:', align='R')
        pdf.cell(0, 7, format_guaranies(total_gastos_personal), align='R')
        pdf.ln()
        pdf.cell(140, 7, 'Total Gastos:', align='R')
        pdf.cell(0, 7, format_guaranies(total_gastos), align='R')
    else:
        pdf.set_font(font_family, '', 11)
        pdf.cell(0, 7, 'No hay gastos registrados', ln=True)
    
    # Guardar en buffer
    pdf_buffer = io.BytesIO()
    pdf.output(pdf_buffer)
    pdf_buffer.seek(0)
    
    # Nombre del archivo
    if mes and anio:
        filename = f'reporte_{get_mes_nombre(mes).lower()}_{anio}.pdf'
    elif anio:
        filename = f'reporte_{anio}.pdf'
    else:
        filename = 'reporte_general.pdf'
    
    return send_file(
        pdf_buffer,
        mimetype='application/pdf',
        as_attachment=False,  # No forzar descarga, permitir compartir
        download_name=filename
    )


# ============================================================================
# INICIALIZACIÓN
# ============================================================================

@app.route('/api/init')
def api_init():
    """Inicializar base de datos"""
    with app.app_context():
        db.create_all()
    return jsonify({'success': True, 'message': 'Base de datos inicializada'})


if __name__ == '__main__':
    with app.app_context():
        db.create_all()
    # Para desarrollo local
    app.run(debug=True, host='0.0.0.0', port=5000)
