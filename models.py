#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Modelos de Base de Datos - Sistema de Gestión de Fábrica
SQLAlchemy para SQLite
"""

from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import func
from datetime import datetime

db = SQLAlchemy()


class Producto(db.Model):
    """Productos fabricados"""
    __tablename__ = 'productos'
    
    id = db.Column(db.Integer, primary_key=True)
    nombre = db.Column(db.String(100), nullable=False)
    stock_actual = db.Column(db.Integer, default=0)
    precio_mayorista = db.Column(db.Integer, default=0)  # En guaraníes
    precio_minorista = db.Column(db.Integer, default=0)  # En guaraníes
    activo = db.Column(db.Boolean, default=True)
    
    # Relaciones
    producciones = db.relationship('Produccion', backref='producto', lazy=True, cascade='all, delete-orphan')
    ventas = db.relationship('Venta', backref='producto', lazy=True)
    
    def to_dict(self):
        return {
            'id': self.id,
            'nombre': self.nombre,
            'stock_actual': self.stock_actual,
            'precio_mayorista': self.precio_mayorista,
            'precio_minorista': self.precio_minorista,
            'activo': self.activo
        }


class Produccion(db.Model):
    """Registro de producción mensual"""
    __tablename__ = 'produccion'
    
    id = db.Column(db.Integer, primary_key=True)
    producto_id = db.Column(db.Integer, db.ForeignKey('productos.id'), nullable=False)
    cantidad = db.Column(db.Integer, nullable=False)
    mes = db.Column(db.Integer, nullable=False)  # 1-12
    anio = db.Column(db.Integer, nullable=False)
    costo_unitario_calculado = db.Column(db.Integer, default=0)  # En guaraníes
    fecha_registro = db.Column(db.DateTime, default=datetime.now)
    
    # Relaciones
    ventas = db.relationship('Venta', backref='produccion', lazy=True)
    
    def to_dict(self):
        return {
            'id': self.id,
            'producto_id': self.producto_id,
            'producto_nombre': self.producto.nombre if self.producto else None,
            'cantidad': self.cantidad,
            'mes': self.mes,
            'anio': self.anio,
            'costo_unitario_calculado': self.costo_unitario_calculado,
            'fecha_registro': self.fecha_registro.isoformat() if self.fecha_registro else None
        }


class Venta(db.Model):
    """Registro de ventas"""
    __tablename__ = 'ventas'
    
    id = db.Column(db.Integer, primary_key=True)
    producto_id = db.Column(db.Integer, db.ForeignKey('productos.id'), nullable=False)
    produccion_id = db.Column(db.Integer, db.ForeignKey('produccion.id'), nullable=False)
    cantidad = db.Column(db.Integer, nullable=False)
    precio_aplicado = db.Column(db.Integer, nullable=False)
    descuento = db.Column(db.Integer, default=0)
    fecha = db.Column(db.DateTime, default=datetime.now)
    mes_venta = db.Column(db.Integer, nullable=False)
    anio_venta = db.Column(db.Integer, nullable=False)
    ganancia_real = db.Column(db.Integer, default=0)
    
    def to_dict(self):
        return {
            'id': self.id,
            'producto_id': self.producto_id,
            'producto_nombre': self.producto.nombre if self.producto else None,
            'produccion_id': self.produccion_id,
            'cantidad': self.cantidad,
            'precio_aplicado': self.precio_aplicado,
            'descuento': self.descuento,
            'fecha': self.fecha.isoformat() if self.fecha else None,
            'mes_venta': self.mes_venta,
            'anio_venta': self.anio_venta,
            'ganancia_real': self.ganancia_real
        }


class Gasto(db.Model):
    """Registro de gastos"""
    __tablename__ = 'gastos'
    
    id = db.Column(db.Integer, primary_key=True)
    concepto = db.Column(db.String(200), nullable=False)
    monto = db.Column(db.Integer, nullable=False)
    fecha = db.Column(db.DateTime, default=datetime.now)
    mes_gasto = db.Column(db.Integer, nullable=False)
    anio_gasto = db.Column(db.Integer, nullable=False)
    tipo = db.Column(db.String(20), nullable=False)  # 'Fabrica' o 'Personal'
    
    def to_dict(self):
        return {
            'id': self.id,
            'concepto': self.concepto,
            'monto': self.monto,
            'fecha': self.fecha.isoformat() if self.fecha else None,
            'mes_gasto': self.mes_gasto,
            'anio_gasto': self.anio_gasto,
            'tipo': self.tipo
        }


# Funciones auxiliares para cálculos financieros

def calcular_costo_unitario_mes(mes, anio):
    """Calcula el costo unitario promedio para un mes específico"""
    gastos_fabrica = db.session.query(func.sum(Gasto.monto)).filter(
        Gasto.mes_gasto == mes,
        Gasto.anio_gasto == anio,
        Gasto.tipo == 'Fabrica'
    ).scalar() or 0
    
    unidades_producidas = db.session.query(func.sum(Produccion.cantidad)).filter(
        Produccion.mes == mes,
        Produccion.anio == anio
    ).scalar() or 0
    
    if unidades_producidas > 0:
        return int(gastos_fabrica / unidades_producidas)
    return 0


def calcular_dinero_total():
    """Calcula el saldo real acumulado (Ingresos - Gastos Totales)"""
    total_ventas = db.session.query(func.sum(
        Venta.precio_aplicado * Venta.cantidad - Venta.descuento
    )).scalar() or 0
    
    total_gastos = db.session.query(func.sum(Gasto.monto)).scalar() or 0
    
    return total_ventas - total_gastos


def calcular_totales_mes(mes, anio):
    """Calcula todos los totales para un mes específico"""
    # Ventas del mes
    ventas_query = db.session.query(func.sum(
        Venta.precio_aplicado * Venta.cantidad - Venta.descuento
    )).filter(Venta.mes_venta == mes, Venta.anio_venta == anio)
    total_ventas = ventas_query.scalar() or 0
    
    # Gastos del mes
    gastos_fabrica = db.session.query(func.sum(Gasto.monto)).filter(
        Gasto.mes_gasto == mes, Gasto.anio_gasto == anio, Gasto.tipo == 'Fabrica'
    ).scalar() or 0
    
    gastos_personal = db.session.query(func.sum(Gasto.monto)).filter(
        Gasto.mes_gasto == mes, Gasto.anio_gasto == anio, Gasto.tipo == 'Personal'
    ).scalar() or 0
    
    # Ganancias del mes
    ganancias = db.session.query(func.sum(Venta.ganancia_real)).filter(
        Venta.mes_venta == mes, Venta.anio_venta == anio
    ).scalar() or 0
    
    return {
        'ventas': total_ventas,
        'gastos_fabrica': gastos_fabrica,
        'gastos_personal': gastos_personal,
        'gastos_total': gastos_fabrica + gastos_personal,
        'ganancias': ganancias,
        'balance': total_ventas - (gastos_fabrica + gastos_personal)
    }


def get_producciones_con_stock(producto_id):
    """Obtiene las producciones de un producto que aún tienen stock disponible"""
    producciones = Produccion.query.filter_by(producto_id=producto_id).all()
    resultado = []
    
    for prod in producciones:
        # Calcular stock vendido de esta producción
        vendido = db.session.query(func.sum(Venta.cantidad)).filter_by(
            produccion_id=prod.id
        ).scalar() or 0
        
        disponible = prod.cantidad - vendido
        
        if disponible > 0:
            resultado.append({
                'id': prod.id,
                'mes': prod.mes,
                'anio': prod.anio,
                'cantidad_total': prod.cantidad,
                'disponible': disponible,
                'costo_unitario': prod.costo_unitario_calculado
            })
    
    return resultado


def get_dashboard_stats():
    """Obtiene estadísticas para el dashboard"""
    from datetime import datetime
    
    mes_actual = datetime.now().month
    anio_actual = datetime.now().year
    
    return {
        'total_productos': Producto.query.filter_by(activo=True).count(),
        'total_produccion': db.session.query(func.sum(Produccion.cantidad)).scalar() or 0,
        'total_ventas': db.session.query(func.sum(Venta.cantidad)).scalar() or 0,
        'dinero_total': calcular_dinero_total(),
        'mes_actual': mes_actual,
        'anio_actual': anio_actual,
        'totales_mes': calcular_totales_mes(mes_actual, anio_actual)
    }
