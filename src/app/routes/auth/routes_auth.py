from flask import Blueprint , render_template , redirect , url_for , flash 
from sqlalchemy.exc import IntegrityError , SQLAlchemyError
from flask_login import logout_user , login_required

from src.app.forms import FormLogin , FormRegister
from src.app.extensions import db
from src.app.services.auth.services_auth import service_login , service_register 

bp = Blueprint('auth' , __name__ , url_prefix='/auth')


@bp.route('/login', methods=['GET','POST'] )
def login():
    form = FormLogin()
    if form.validate_on_submit():

        username = form.username.data
        password = form.password.data

        user = service_login( db.session , username , password )
        
        if user:
            if user.is_admin:
                return redirect(url_for('admin.view_orders'))
            return redirect(url_for('user.order'))
        
    return render_template('auth/login.html' , form = form )


@bp.route('/register' , methods=['GET','POST'])
def register():
    form = FormRegister()
    if form.validate_on_submit():

        username = form.username.data
        password = form.password.data

        try:
            service_register(db.session , username , password)
            db.session.commit()
            flash('¡Registro exitoso!' , 'succes')
            return redirect(url_for('auth.login'))

        except ( IntegrityError , SQLAlchemyError) as e:
            db.session.rollback()
            flash('Usuario o Contraseña Incorrecto', 'danger')

    return render_template('auth/register.html' , form = form )


@bp.route('/logout')
@login_required
def logout():
    logout_user()
    flash('Has cerrado la sesion')
    return redirect(url_for('auth.login'))