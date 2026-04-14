from flask_wtf import FlaskForm
from wtforms  import StringField , PasswordField , SubmitField
from wtforms.validators import DataRequired , Length 
from src.app.utils.form_helpers import strip_value



class FormRegister(FlaskForm):
    username = StringField(
        'Username:',
        validators=[
            DataRequired( message="Esta opción es obligatoria" ), 
            Length( min=10 , max=20 ) ],
        filters=[strip_value]
    )

    password = PasswordField(
        'Password:',
        validators=[
            DataRequired( message="Esta opción es obligatoria" ),
            Length(min=8 , max=20)],
        filters=[strip_value]
    )

    submit = SubmitField('Registrar')