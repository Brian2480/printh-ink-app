# Printh-Ink_App

Plataforma en la cual el usuario se registra para despues poder realizar un pedido para ser impreso en DTF enviando su archivo en pdf,
al momento de realizar su pedido en automatico se mostrara la medida, el estatus del pedido(por pagar y pagado) y el costo 
que en un principio por default sera: $200 hasta que el administrador cambie el precio segun el cliente(esto solo es una unica ves al ser cliente nuevo).
Al subir la captura de su pago en Adelanto el estatus seguira en  "por pagar" pero si la sube a "Liquidacion" al administrador se le desbloqueara la
opcion de cambiar el status a pagado una ves corroborado la totalidad del pago.

El administrador en su panel podra ver la cantidad de clientes registrados y cambiar el precio de cada uno segun sea necesario

## 🛠️ Tecnologías
* **Lenguaje:** Python 3.13.1
* **Framework:** Flask, SQLAlchemy
* **Estilos:** Bootstrap 5,CSS3, HTML 5

## 📦 Instalación
Para tener una copia local, sigue estos pasos:
1. `git clone https://github.com/Brian2480/Printh-Ink_App.git`
2. `cd Printh_App`
3. `pip install -r requirements.txt`

## 📸 Demo
| Vista de Usuario | Panel de Administración |
| :---: | :---: |
| ![Inicio](src/app/static/img/registro.jpg) | ![Admin](src/app/static/img/crear.jpg) |


## ✒️ Autor
* **Brian** - [Brian2480](https://github.com/Brian2489)
