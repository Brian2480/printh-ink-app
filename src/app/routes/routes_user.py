import cloudinary
import cloudinary.uploader
from decimal import Decimal
from flask import Blueprint, render_template, redirect, url_for, flash, current_app
from flask_login import login_required, current_user
from sqlalchemy.exc import IntegrityError , SQLAlchemyError
from werkzeug.exceptions import NotFound

from src.app.extensions import db
from src.app.forms.form_upload import FormUploadOrder, FormUploadAdvance, FormUploadPay
from src.app.services.services_user import (
                                                UploadService, 
                                                service_order, 
                                                service_get_all_orders, 
                                                service_delete_specific_file,
                                                service_delete_order
                                            )

bp = Blueprint('user' , __name__ , url_prefix='/my')

@bp.route('/order')
@login_required
def order():
    return render_template('user/order.html')


@bp.route('/orders')
@login_required
def orders():
    form_pay=FormUploadPay()
    form_adv=FormUploadAdvance()
    
    user_orders = service_get_all_orders(
        db_session=db.session, 
        user_id=current_user.id)
    
    return render_template('user/orders.html', user_orders=user_orders, form_adv=form_adv, form_pay=form_pay)


@bp.route('/upload/order' , methods=['GET', 'POST'] )
@login_required
def upload_pdf():
    form = FormUploadOrder()
    if form.validate_on_submit():
        file_to_upload = form.document.data
        try:
            upload_result = cloudinary.uploader.upload(
                file_to_upload,
                resource_type = 'auto',
                folder = 'mis_documentos',
                image_metadata = True,
            )

            # 1. Intentamos sacar la medida REAL de los metadatos de Photoshop primero
            meta = upload_result.get('image_metadata', {})
            embedded = upload_result.get('embedded_images', [{}])[0]
            url = upload_result.get('secure_url')
            public_id = upload_result.get('public_id')

            # Prioridad: 1. ExifHeight, 2. EmbeddedHeight, 3. RootHeight

            real_width = Decimal(str(
            meta.get('ExifImageWidth') or 
            embedded.get('width') or 
            upload_result.get('width')
            ))

            real_height = Decimal(str(
                meta.get('ExifImageHeight') or 
                embedded.get('height') or 
                upload_result.get('height')
            ))

            medida_larga_px = max(real_width, real_height)

            # 2. Sacamos los DPI (XResolution es 200 en tu JSON)
            dpi = Decimal(str(meta.get('XResolution') or 72))

            # 3. Cálculo Maestro
            pdf_meters = (medida_larga_px / dpi * Decimal('2.54') / Decimal('100')).quantize(Decimal('0.01'))

            print(f"Medida real detectada: {pdf_meters}m") # Ahora sí dirá 2.0m

            new_order = service_order( db_session=db.session, 
                                    user_id=current_user.id, 
                                    meters=pdf_meters)

            UploadService.save_upload_data(
                db_session=db.session, 
                order_id=new_order.id, 
                file_url=url, 
                public_id=public_id, 
                file_type='pdf')

            db.session.commit()
            return redirect(url_for('user.orders'))
        
        except NotFound as e:
            db.session.rollback()
            flash(str(e), 'danger')

        except SQLAlchemyError as e:
            db.session.rollback()
            flash(f'Hubo un error en la base de datos', 'danger')

    return render_template('user/upload.html' , form = form )


@bp.route('/upload/advance/<int:order_id>', methods=['GET','POST'])
@login_required
def upload_advance(order_id):
    form=FormUploadAdvance()
    if form.validate_on_submit():
        file_to_upload = form.document_advance.data
        try:

            upload_result = cloudinary.uploader.upload(
                file_to_upload,
                resource_type = 'auto',
                folder = 'mis_advance',
                image_metadata = True,
                ) 

            url = upload_result.get('secure_url')
            public_id = upload_result.get('public_id')

            if url and public_id:
            
                UploadService.save_upload_data(
                    db_session=db.session,
                    order_id=order_id,
                    file_url=url,
                    public_id=public_id,
                    file_type='advance'
                )

                db.session.commit()
                return redirect(url_for('user.orders'))
            
            else:
                flash('No se pudo obtener la respuesta del servidor de imágenes', 'danger')

        except IntegrityError as e:
            db.session.rollback()
            flash('Error no se pudo vincular el pago a la orden', 'danger')
            print(f'Error: {e}')

        
        except SQLAlchemyError as e:
            flash('Error en la base de datos', 'danger')
            print(f'Error: {e}')

    return render_template('user/orders.html', form=form)


@bp.route('/upload/pay/<order_id>', methods=['GET', 'POST'])
@login_required
def upload_pay(order_id):
    form=FormUploadPay()
    if form.validate_on_submit():
        file_to_upload = form.document_pay.data
        try:

            upload_result = cloudinary.uploader.upload(
                file_to_upload,
                resource_type = 'auto',
                folder = 'mis_pay',
                image_metadata = True,
                ) 

            url = upload_result.get('secure_url')
            public_id = upload_result.get('public_id')

            if url and public_id:
            
                UploadService.save_upload_data(
                    db_session=db.session,
                    order_id=order_id,
                    file_url=url,
                    public_id=public_id,
                    file_type='pay'
                )

                db.session.commit()
                return redirect(url_for('user.orders'))
            
            else:
                flash('No se pudo obtener la respuesta del servidor de imágenes', 'danger')

        except IntegrityError:
            db.session.rollback()
            flash('Error no se pudo vincular el pago a la orden', 'danger')
        
        except SQLAlchemyError:
            flash('Error en la base de datos', 'danger')

    return render_template('user/orders.html', form=form)
        

@bp.route('/delete/upload/advance/<int:document_id>/<string:type_document>', methods=['POST'])
@login_required
def delete_upload(document_id, type_document):

    try:
        service_delete_specific_file(
            db_session = db.session, 
            document_id=document_id, 
            type_document=type_document
        )
        
        db.session.commit()
        flash("El archivo se eliminó de la nube y la base de datos.", "success")
    
    except NotFound as e:
        db.session.rollback()
        current_app.logger.error(f"Error de BD: {e}")
        flash(str(e),"warning")

    except SQLAlchemyError as e:
        db.session.rollback()
        current_app.logger.error(f"Error crítico: {e}")
        flash("Ocurrio un error inesperado", "danger")

    return redirect(url_for('user.orders'))


@bp.route('/delete/order/<int:order_id>', methods=['POST'] )
@login_required
def delete_order(order_id):
    
    try:
        service_delete_order(
            db_session=db.session, 
            order_id=order_id, 
        )

        db.session.commit()
        flash("Orden eliminada", 'succes')

    except NotFound as e:
        db.session.rollback()
        current_app.logger.error(f'Error de BD: {e}')
        flash(str(e), "warningr")
    
    except SQLAlchemyError as e:
        db.session.rollback()
        current_app.logger.error(f"Error crítico: {e}")
        flash("Ocurrio un error inesperado", "danger")

    return redirect(url_for('user.orders'))