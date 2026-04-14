from datetime import datetime, timedelta
from typing import cast
from io import BytesIO
from openpyxl import Workbook
from openpyxl.worksheet.worksheet import Worksheet
from sqlalchemy import select, func, and_
from sqlalchemy.orm import joinedload, selectinload

from src.app.models import User, Order

def service_get_all_clients(db_session):
    stmt = select(User).options(selectinload(User.orders))
    clients = db_session.execute(stmt).scalars().all()
    return clients


def service_get_order_client(db_session, id_order):
    order = db_session.get(Order, id_order)
    return order


def service_get_orders_day(db_session, select_day):
    # --- PASO 1: Inteligencia en Python (Casi instantáneo) ---
    today = datetime.now()
    # Calculamos el inicio de ESTA semana (el domingo pasado)
    start_of_week = today - timedelta(days=int(today.strftime('%w')))
    # Calculamos el día específico que pidió el usuario
    target_date = start_of_week + timedelta(days=int(select_day))
    
    # Definimos el rango exacto de 24 horas
    start_day = target_date.replace(hour=0, minute=0, second=0, microsecond=0)
    end_day = target_date.replace(hour=23, minute=59, second=59, microsecond=999999)

    # --- PASO 2: Fuerza Bruta en la Base de Datos (Máximo Performance) ---
    stmt = (
        select(Order)
        .options(joinedload(Order.user), joinedload(Order.uploads))
        .where(
            # La BD solo busca registros dentro de estas dos marcas de tiempo
            and_(
                Order.created_at >= start_day,
                Order.created_at <= end_day
            )
        )
        .order_by(Order.created_at.asc())
    )
    
    # La BD solo nos devuelve los registros que cumplen la condición. 
    # Python no tiene que filtrar nada después.
    result = db_session.execute(stmt)
    return result.unique().scalars().all()


def service_update_amount(order, amount, a_belong, t_belong, belong_at):

    if belong_at == 'advance':
        order.advance = amount
        order.a_belong = a_belong
    
    elif belong_at =='pay':
        order.t_belong = t_belong


def service_status_payment(order, payment):
    order.paid = payment


def export_orders_by_weekday(db_session, Order, day_id: int):
    wb = Workbook()
    ws = cast(Worksheet, wb.active)
    
    # 1. Calcular la fecha real basada en el day_id de esta semana
    hoy = datetime.now().date()
    # weekday() de Python: Lun=0 ... Dom=6. 
    # Tu lista en HTML: Dom=0, Lun=1... (Ajustamos el desfase)
    dia_actual_semana = hoy.weekday() + 1 if hoy.weekday() < 6 else 0
    diferencia = day_id - dia_actual_semana
    fecha_destino = hoy + timedelta(days=diferencia)
    ws.title = f"Reporte {fecha_destino.strftime('%d-%m')}"
    
    # 2. Encabezados
    headers = ["Fecha","Cliente", "Precio", "Cantidad", "Total","Adelanto","F.P","Liquidación","F.P","Status"]
    ws.append(headers)
    
    # 3. Consulta filtrando por la fecha calculada
    stmt = select(Order).filter(func.date(Order.created_at) == fecha_destino)
    orders = db_session.execute(stmt).scalars().all()
    if not orders:
        return None, fecha_destino
        
# ... (dentro del bucle for o in orders) ...
    for o in orders:
        # Convertimos el booleano 'paid' a un texto amigable
        estado_pago = "Pagado" if o.paid else "Pendiente"
        
        row = [
            o.created_at.strftime("%d/%m"),
            o.user.username,
            float( o.price),
            o.meters,
            float(o.cost),
            o.advance,
            o.a_belong,
            float(o.total),
            o.t_belong,
            estado_pago, 
        ]

        ws.append(row)
    output = BytesIO()
    wb.save(output)
    output.seek(0)
    
    return output, fecha_destino