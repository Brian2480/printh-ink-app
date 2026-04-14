from flask_wtf import FlaskForm
from wtforms import DecimalField, SubmitField
from wtforms.validators import DataRequired, NumberRange

from src.app.utils.form_helpers import strip_value


class FormEditPrice(FlaskForm):
    price = DecimalField(
        'Price',
        validators=[
            DataRequired(message='El precio es Obligatorio'),
            NumberRange(min=150,max=200, message='El costo no puede ser menor a 150')
            ],
            places=2,
    )


    submit = SubmitField('Guardar')