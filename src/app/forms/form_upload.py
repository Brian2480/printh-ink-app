from flask_wtf import FlaskForm
from flask_wtf.file import FileField , FileRequired , FileAllowed
from wtforms import SubmitField


class FormUploadOrder(FlaskForm):
    document = FileField(
        'Documento',
        validators=[
            FileRequired(message='Campo Obligatorio'),
            FileAllowed(['jpg','pdf','png'] , message='Formato Invalido' )
            ]
    )

    submit = SubmitField('Subir')


class FormUploadAdvance(FlaskForm):
    document_advance = FileField(
        'Documento',
        validators=[
            FileRequired(message='Campo Obligatorio'),
            FileAllowed(['jpg'] , message='Formato Invalido solo: ".jpg" ' )
            ]
    )
    

class FormUploadPay(FlaskForm):
    document_pay = FileField(
        'Documento',
        validators=[
            FileRequired(message='Campo Obligatorio'),
            FileAllowed(['jpg'] , message='Formato Invalido solo: ".jpg" ' )
            ]
    )

