from flask import Flask, render_template, request, redirect
from flask_mysqldb import MySQL
from datetime import datetime #PARA AGREGAR LA FECHA AL NOMBRE DE LA FOTO CUANDO SE GUARDA
import os  #PARA HACER EL UPDATE DE LA FOTO 

app= Flask (__name__)

#CONEXIÒN CON LA BASE DE DATOS************************
mysql=MySQL(app)

app.config['MYSQL_HOST'] = 'localhost'
app.config['MYSQL_USER'] = 'root'
app.config['MYSQL_PASSWORD'] = ''
app.config['MYSQL_DB'] = 'sistema_empleados'

CARPETA = os.path.join('uploads') #PARA HACER UPDATE DE LA FOTO
app.config['CARPETA']=CARPETA

@app.route('/')
def index():
    sql="SELECT * FROM `empleados`;"
    conn = mysql.connection
    cursor=conn.cursor()
    cursor.execute(sql)
    empleados = cursor.fetchall()    
    conn.commit()
    return render_template('empleados/index.html', empleados=empleados)

#ELIMINAR REGISTROS
@app.route('/destroy/<int:id>')
def destroy(id):
    conn = mysql.connection
    cursor = conn.cursor()
    cursor.execute("DELETE FROM empleados WHERE id= %s",(id,))
    conn.commit()
    return redirect('/')

#EDITAR REGISTROS
@app.route('/edit/<int:id>')
def edit(id):
    conn = mysql.connection
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM empleados WHERE id=%s", (id,))
    empleados = cursor.fetchall()
    conn.commit()
    print(empleados)
    return render_template('empleados/edit.html',empleados=empleados)

#UPDATE
@app.route('/update', methods=['POST'])
def update():
    _nombre = request.form['txtNombre']
    _correo = request.form['txtCorreo']
    _foto = request.files['txtFoto']
    id = request.form['txtId']

    conn = mysql.connection
    cursor = conn.cursor()

    # Obtener la foto existente para eliminarla más tarde
    cursor.execute("SELECT foto FROM empleados WHERE id=%s", (id,))
    fila = cursor.fetchall()

    # Inicializar la variable fuera de la condición
    nuevoNombreFoto = None

    if _foto.filename != '':
        # Si hay una nueva foto, asignar un nuevo nombre
        now = datetime.now()
        tiempo = now.strftime("%Y%H%M%S")
        nuevoNombreFoto = tiempo + _foto.filename

        # Guardar la nueva foto
        _foto.save(os.path.join(app.config['CARPETA'], nuevoNombreFoto))

        if fila:
            # Si hay una fila, hay una foto existente que podemos eliminar
            os.remove(os.path.join(app.config['CARPETA'], fila[0][0]))

    # Si no hay una nueva foto, nuevoNombreFoto se mantiene como None

    # Actualizar la base de datos, incluso si no hay una nueva foto
    sql = "UPDATE empleados SET nombre=%s, correo=%s, foto=%s WHERE id=%s;"
    datos = (_nombre, _correo, nuevoNombreFoto, int(id))
    cursor.execute(sql, datos)
    conn.commit()
    return redirect('/')

#CREAR REGISTROS
@app.route('/create')
def create():
    return render_template('empleados/create.html')

@app.route('/store', methods=['POST'])
def storage():
    _nombre=request.form['txtNombre']
    _correo=request.form['txtCorreo']
    _foto=request.files['txtFoto']

    #Para guardar la foto que carga el usuario
    now = datetime.now()
    tiempo = now.strftime("%Y%H%M%S")

    if _foto.filename!='':
        nuevoNombreFoto = tiempo + _foto.filename
        _foto.save("uploads/" +nuevoNombreFoto)


    sql="INSERT INTO `empleados` (`id`, `nombre`, `correo`, `foto`) VALUES (NULL, %s, %s, %s);"

    datos=(_nombre, _correo, nuevoNombreFoto) #**********************************

    conn = mysql.connection
    cursor=conn.cursor()
    cursor.execute(sql, datos)
    conn.commit()
    return redirect('/')


if __name__ == '__main__':
    app.run(debug=True)