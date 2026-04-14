import cloudinary.uploader
from decimal import Decimal
from sqlalchemy import select
from sqlalchemy.orm import joinedload
from werkzeug.exceptions import NotFound

from src.app.models.model import Upload , Order, User


class UploadService:

    @staticmethod
    def save_upload_data(db_session, order_id, file_url, public_id, file_type):
        """
        Busca o crea el registro de subidas y actualiza la orden si es necesario.
        """
        # 1. Buscar si ya existe un registro de Upload para esta orden
        stmt_upload = select(Upload).filter_by(order_id=order_id)
        upload_record = db_session.execute(stmt_upload).scalar_one_or_none()

        # 2. Si no existe, creamos uno nuevo
        if not upload_record:
            upload_record = Upload(order_id=order_id)
            db_session.add(upload_record)

        # 3. Asignar datos según el tipo de archivo
        if file_type == 'pdf':
            upload_record.pdf_url = file_url
            upload_record.pdf_public_id = public_id
            
        elif file_type == 'advance':
            upload_record.jpg_advance_url = file_url
            upload_record.jpg_advance_public_id = public_id
            
        elif file_type == 'pay':
            upload_record.jpg_pay_url = file_url
            upload_record.jpg_pay_public_id = public_id
            
            # --- LÓGICA DE NEGOCIO EXTRA ---
            # Si suben el pago final, buscamos la orden y cambiamos su estado
            stmt_order = select(Order).filter_by(id=order_id)
            order_record = db_session.execute(stmt_order).scalar_one_or_none()
            
            if order_record:
                order_record.status = 'Pagado' # O el nombre de estado que uses

        return upload_record


def service_order(db_session, user_id, meters):

    client = db_session.get(User, user_id)

    if client is None:
        raise NotFound(f"Error: El cliente con ID {user_id} no existe.")

    new_order = Order(
        user_id=user_id,
        price=client.custom_price,
        meters=meters,
        advance=Decimal('00.00'),

    )
    db_session.add(new_order)
    db_session.flush()
    return new_order


def service_get_all_orders(db_session, user_id):
    stmt = select(Order).options(joinedload(Order.uploads)).filter_by(user_id=user_id).order_by(Order.created_at.asc())
    user_orders = db_session.execute(stmt).scalars().unique().all()
    return user_orders


def service_get_order_id(db_session, user_order_id):
    stmt = select(Order).filter_by(id=user_order_id)
    user_order_id = db_session.execute(stmt).scalar_one_or_none()
    return user_order_id


def service_delete_specific_file(db_session, document_id, type_document):

    document = db_session.get(Upload, document_id)

    if not document:
        raise NotFound(f"Error: El documento {document} no existe.")

    if type_document == 'advance':
        cloudinary.uploader.destroy(document.jpg_advance_public_id)
        document.jpg_advance_url = None
        document.jpg_advance_public_id = None

    elif type_document == 'pay':
        cloudinary.uploader.destroy(document.jpg_pay_public_id)
        document.jpg_pay_url = None
        document.jpg_pay_public_id = None

    return True


def service_delete_order(db_session, order_id):

    order = db_session.get(Order, order_id)

    if not order:
        raise NotFound(f'No se pudo eliminar: La orden #{order_id} no existe')

    if order.uploads:
        public_ids = [
            order.uploads.pdf_public_id,
            order.uploads.jpg_advance_public_id,
            order.uploads.jpg_pay_public_id
        ]

        for pid in public_ids:
            if pid:
                cloudinary.uploader.destroy(pid)

    db_session.delete(order)



