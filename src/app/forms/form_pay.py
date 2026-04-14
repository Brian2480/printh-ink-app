from decimal import Decimal

from flask_wtf import FlaskForm
from wtforms import SelectField, DecimalField
from wtforms.validators import Optional, NumberRange, DataRequired


class FormOfPayment(FlaskForm):
    
    a_belong = SelectField(
        'Forma de Pago', 
        choices=[
            ('S/A', 'S/A'),
            ('T.M', 'T.M'),
            ('T.F', 'T.F'),
            ('T.J', 'T.J'),
            ('EFE', 'EFE')
            
        ], 
        validators=[Optional()])
    
    t_belong = SelectField(
        'Forma de Pago', 
        choices=[
            ('S/A', 'S/A'),
            ('T.M', 'T.M'),
            ('T.F', 'T.F'),
            ('T.J', 'T.J'),
            ('EFE', 'EFE')
            
        ], 
        validators=[Optional()])

    advance = DecimalField(
        'Cantidad:',
        validators=[
            Optional(), 
            NumberRange(min=0,max=7000)
        ],
        places=2,
    )
