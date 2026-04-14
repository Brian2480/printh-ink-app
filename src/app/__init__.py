from flask import Flask
from src.config.settings import ConfigClass
from src.app.extensions import db
from src.app.extensions import login_manager , init_cloudinary
from src.app.commands.commands import create_admin

def create_app():
    app = Flask(__name__)
    app.config.from_object(ConfigClass)

    #Inicializar Extensuiones
    db.init_app(app)
    login_manager.init_app(app)
    init_cloudinary(app)
    app.cli.add_command(create_admin)

    #Configuracion de Flask Login
    login_manager.login_view = 'auth.login' #type: ignore
    login_manager.login_message = 'Debes iniciar sesión'
    login_manager.login_message_category = 'info'

    with app.app_context():
        from src.app.models import User

        @login_manager.user_loader
        def user_loader(user_id):
            return db.session.get(User , int(user_id))

        if app.config.get('AUTO_CREATE_TABLES'):
            db.create_all()

    from src.app.routes.routes_public import bp as bp_public
    app.register_blueprint(bp_public)

    from src.app.routes.auth.routes_auth import bp as bp_auth
    app.register_blueprint(bp_auth)

    from src.app.routes.routes_user import bp as bp_user
    app.register_blueprint(bp_user)

    from src.app.routes.routes_admin import bp as bp_admin
    app.register_blueprint(bp_admin)

    return app