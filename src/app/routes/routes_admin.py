from datetime import date

from flask import Blueprint, render_template, redirect, url_for, flash, abort, request, send_file, current_app
from flask_login import login_required
from sqlalchemy.exc import IntegrityError, SQLAlchemyError

from src.app.extensions import db
from src.app.services.services_admin import (service_get_all_clients, 
                                            service_get_order_client, 
                                            service_get_orders_day,
                                            service_update_amount,
                                            service_status_payment,
                                            export_orders_by_weekday )

from src.app.forms.form_price import FormEditPrice 
from src.app.forms.form_pay import FormOfPayment
from src.app.models.model import Order


bp = Blueprint('admin', __name__, url_prefix='/admin')


@bp.app_template_filter('strfdate')
@login_required
def strfdate_filter(value, format='%d/%m/%Y %H:%M'):
    if value is None:
        return ""
    return value.strftime(format)


@bp.route('/view/clients')
@login_required
def clients():
    clients = service_get_all_clients(db_session=db.session)
    return render_template('admin/clients.html', clients=clients)


@bp.route('/edit/price/<int:id_order>', methods=['GET', 'POST'])
@login_required
def edit_price(id_order):

    orders = service_get_order_client(db_session=db.session, id_order=id_order)
    if not orders:
        abort(404)

    form = FormEditPrice(obj=orders)
    
    if form.validate_on_submit():
        try:
            form.populate_obj(orders)

            if orders.user:
                orders.user.custom_price = orders.price
                
            db.session.commit()
            flash('Cambio realizado', 'success')
            return redirect(url_for('admin.clients'))

        except IntegrityError as e:
            db.session.rollback()

        except SQLAlchemyError as e:
            db.session.rollback()

    return render_template('admin/edit_price.html', orders=orders, form=form)


@bp.route('/view/orders/day')
@login_required
def view_orders():

    form = FormOfPayment()
    #Obtener datos de la url 
    default_actual_day = date.today().strftime('%w')
    select_day = request.args.get( 'day' , default=default_actual_day, type=str)

    todo = service_get_orders_day(db_session=db.session, select_day=select_day)

    return render_template('admin/orders.html', todo=todo, day_id=select_day, form=form )


@bp.route('/edit/amount/<int:id_order>/<string:belong_at>/<string:day>', methods=['GET', 'POST'])
@login_required
def edit_amount(id_order,belong_at,day):

    orders = service_get_order_client(db_session=db.session, id_order=id_order)
    if not orders:
        abort(404)

    form = FormOfPayment()
    
    if form.validate_on_submit():

        amount = form.advance.data
        a_belong = form.a_belong.data
        t_belong = form.t_belong.data

        try:
            
            service_update_amount(
                order=orders, 
                amount=amount, 
                a_belong=a_belong, 
                t_belong=t_belong,
                belong_at=belong_at
            )
            
            db.session.commit()
            db.session.refresh(orders)
            
            flash('Cambio realizado con exito', 'success')
            print(f'{day}')
            return redirect(url_for('admin.view_orders', day=day))

        except IntegrityError as e:
            db.session.rollback()
            print(f'Error {e}')

        except SQLAlchemyError as e:
            db.session.rollback()
            print(f'Error {e}')

    return render_template('admin/orders.html', orders=orders, form=form)


@bp.route('/order/payment/<int:id_order>/<int:payment>/<int:day>', methods=['GET','POST'])
@login_required
def payment_status(id_order, payment,day):

    order = service_get_order_client(db_session=db.session, id_order=id_order)

    if not order:
        abort(404)

    try:
        service_status_payment(order=order, payment=payment)
        db.session.commit()

    except SQLAlchemyError as e:
        db.session.rollback()
        flash(f"Error al actualizar","danger")

    return redirect(url_for('admin.view_orders',day=day))


@bp.route('/download-excel', methods=['GET'])
@login_required
def download_excel():
    # El day_id viene del form como string, lo pasamos a int
    day_id_raw = request.args.get('day', 0)
    
    try:
        day_id = int(day_id_raw)
        
        # El servicio ahora devuelve el archivo Y la fecha calculada
        excel_file, fecha_calculada = export_orders_by_weekday(
            db.session, Order, day_id
        )

        if not excel_file:
            flash(f"No hay órdenes para el {fecha_calculada.strftime('%A %d/%m')}", "info")
            return redirect(url_for('admin.view_orders', day=day_id))

        nombre_archivo = f"Reporte_{fecha_calculada.strftime('%d-%b')}.xlsx"

        return send_file(
            excel_file,
            mimetype="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
            as_attachment=True,
            download_name=nombre_archivo
        )

    except Exception as e:
        db.session.rollback()
        current_app.logger.error(f"Error Excel: {e}")
        flash("Error al generar el archivo", "danger")
        return redirect(url_for('admin.view_orders'))
