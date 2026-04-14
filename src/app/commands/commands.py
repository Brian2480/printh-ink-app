import click
from flask.cli import with_appcontext
from sqlalchemy import select

from src.app.extensions import db
from src.app.models.model import User

@click.command('create-admin')
@click.argument('username')
@click.argument('password')
@with_appcontext
def create_admin(username, password):
    """
    Comando para crear el administrador único del sistema.
    Uso: flask create-admin <usuario> <password>
    """
    # 1. Verificar si ya existe algún usuario en la tabla
    stmt = select(User).where(User.is_admin==True).limit(1)
    admin_exists = db.session.scalar(stmt)
    
    if admin_exists:
        click.echo(click.style("Error: Ya existe un administrador. No se pueden crear más.", fg="red"))
        return

    try:
        # 2. Crear instancia del modelo
        # Nota: Asegúrate de que tu modelo User tenga el método set_password
        new_admin = User(
            username=username,
            is_admin=True
        )
        new_admin.set_password(password)

        # 3. Guardar en la base de datos
        db.session.add(new_admin)
        db.session.commit()
        
        click.echo(click.style(f"Éxito: Administrador '{username}' creado correctamente.", fg="green"))
    
    except Exception as e:
        db.session.rollback()
        click.echo(click.style(f"Error técnico: {e}", fg="red"))