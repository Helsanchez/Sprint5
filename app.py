
from flask import Flask, render_template,request,session,redirect,url_for
from werkzeug.security import generate_password_hash,check_password_hash
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
import smtplib
import sqlite3
import sqlite3 as sql

app = Flask(__name__)
msg = MIMEMultipart()

@app.route('/')
def home():
    return redirect(url_for("acceso"))

@app.route('/acceso')
def acceso():
    return render_template('inicio.html')

@app.route('/inicio', methods=['POST'])
def inicio():
    Contrasena=""
    usuario = request.form['user']
    passw = request.form['pass']
    conexion = sqlite3.connect("usuarios.db")
    conexion.row_factory = sql.Row
    objcursor = conexion.cursor()
    objcursor.execute("select Contrasena from registro where Usuario = '"+usuario+"'")
    rows = objcursor.fetchone()
    print(rows)
    if rows != None and len(rows)>0 and check_password_hash(rows["Contrasena"],passw):
        session['login'] = True
        session['user'] = usuario
        return redirect(url_for("ultimosB"))
    else:
        mensaje = 'Por favor ingresa usuario y contraseña validos'
        return render_template('inicio.html', mensaje = mensaje)


@app.route('/regis')
def regis():
    return render_template("registro.html")

@app.route('/guardar', methods=['POST'])
def guardar():
    conexion = sqlite3.connect("usuarios.db")
    try:
        nombre = request.form['nombre']
        contacto = request.form['contacto']
        correo = request.form['correo']
        usuario = nombre[0:1] + '.' + nombre
        contrasena = nombre[0:7]
        contra_hash = generate_password_hash(contrasena)
        conexion.execute("insert into registro(Nombre,Contacto,Correo,Usuario,Contrasena,Frase) values (?,?,?,?,?,?)" ,(nombre,contacto,correo,usuario,contra_hash,contrasena))
        conexion.commit()
        mensaje = 'Registro éxitoso, su usuario es: '+usuario+"\nTu contraseña es: "+contrasena
    except Exception as e:
        print(e)
        mensaje = e
    finally: 
        conexion.close()
    return render_template('registro.html', mensaje = mensaje)

@app.route('/cont')
def cont():
    return render_template("recuperarcontraseña.html")

@app.route('/recuperar',methods=['POST'])
def recuperar():
    Contrasena =""
    correo = request.form['correo']
    conexion = sqlite3.connect("usuarios.db")
    conexion.row_factory = sql.Row
    objcursor = conexion.cursor()
    objcursor.execute("select * from registro where Correo = '"+correo+"'")
    rows = objcursor.fetchone()
    if rows != None and len(rows)>0:
        Frase=rows["Frase"]
        Nombre= rows["Nombre"]
        Contacto=rows["Contacto"]
        Usuario=rows["Usuario"]     
        message_e='Buen dia, a continuacion adjunto la informacion suministrada durante su registro: '+"\nUsuario: "+Usuario+"\nContraseña: "+ Frase +"\nNombre: " +Nombre
            #new line \n
            #parametros de conexión del correo electronico
        password = "grupo2020"
        msg['From'] = "grupoenemasvirgulilla2020@gmail.com"
        msg['To'] = correo
        msg['Subject'] = "Recuperacion de contraseña"
            # Cuerpo del mensaje se escoje texto plano
        msg.attach(MIMEText(message_e, 'plain'))
            #establecer conexión con el servidor en este caso gmail
        server = smtplib.SMTP('smtp.gmail.com: 587')
        server.starttls()
            #autenticación de las credenciales de correo con el servidor de gmail
        server.login(msg['From'], password)
            #enviar el mensaje aap travez del servidor de correo de gmail
        server.sendmail(msg['From'], msg['To'], msg.as_string())
        server.quit()#cerrar la conexión con el ser
        return render_template('recuperarcontraseña.html',mensaje='Se ha enviado su clave y su informacion a su coreo '+correo)
    else:
        return render_template('recuperarcontraseña.html', mensaje='Validación no exitosa')

app.secret_key = '1234'

@app.route('/ultimosB')
def ultimosB():
    if 'user' in session:
        conexion = sqlite3.connect("usuarios.db")
        conexion.row_factory = sql.Row
        objcursor = conexion.cursor()
        objcursor.execute("select * from nuevoBlog")   
        rows = objcursor.fetchall()
        rows.reverse()
        return render_template("ultimosB.html",rows = rows)
    else:
        mensaje="Debes iniciar sesion"
        return render_template('inicio.html',mensaje=mensaje)

@app.route('/busqueda')
def busqueda():
    if 'user' in session:
        return redirect(url_for('busqueda.html'))
    else:
        mensaje="Debes iniciar sesion"
        return render_template('inicio.html',mensaje=mensaje)

@app.route('/busque',methods=['POST'])
def busque():
    contador = 0
    if 'user' in session:
        busca=request.form["busca"]
        conexion = sqlite3.connect("usuarios.db")
        conexion.row_factory = sql.Row
        objcursor = conexion.cursor()
        objcursor.execute("select * from nuevoBlog where tema like '%"+busca+"%'")   
        rows = objcursor.fetchall()
        rows.reverse()
        for i in rows:
            contador = contador + 1        
        if (contador > 0):
            return render_template('busqueda.html', rows=rows)
        else:
            mensaje = 'Por favor ingresa una busqueda valida'
            return render_template('ultimosB', mensaje = mensaje)
    else:
        mensaje="Debes iniciar sesion"
        return render_template('inicio.html',mensaje=mensaje)


@app.route('/logout')
def logout():
    if 'user' in session:
        session.clear()
        session.pop('user', None)
        return redirect(url_for('acceso'))
    else:
        return render_template('inicio.html',mensaje='Debes iniciar primero sesíon')


@app.route('/leer', methods=['POST'])
def leer():
    if 'user' in session:
        idblog = request.form['idblog']
        conexion = sqlite3.connect("usuarios.db")
        conexion.row_factory = sql.Row
        objcursor = conexion.cursor()
        objcursor.execute("select * from nuevoBlog where idblog = " + idblog)   
        rows = objcursor.fetchone()
        objcursor.execute("select * from Comentarios where idblog = " + idblog)
        coms = objcursor.fetchall()
        if rows ['estado'] == ("Publico"):
            return render_template("leer.html",row = rows,coms=coms)
        else:
            mensaje = ("Este blog es privado, por lo que su lectura esta restringida")
            return render_template("leerp.html",row = rows,mensaje=mensaje)
    else:
        return render_template('inicio.html',mensaje='Debes iniciar primero sesíon')

@app.route('/comentarios', methods=['POST'])
def comentarios():
    if 'user' in session:  
        com = request.form['comentario']
        idbl = request.form['idblog']
        user = session['user']
        fecha = "2020-22-12"

        conexion = sqlite3.connect("usuarios.db")
        conexion.row_factory = sql.Row
        objcursor = conexion.cursor()
        objcursor.execute("INSERT INTO Comentarios (idblog,idusuario,fecha,comentario) VALUES (?,?,?,?)",(idbl,user,fecha,com))
        conexion.commit() 
        return redirect(url_for("ultimosB"))
    else:
        return render_template('inicio.html',mensaje='Debes iniciar primero sesíon')
        
@app.route('/misb')
def misb():
    if 'user' in session:
        conexion = sqlite3.connect("usuarios.db")
        conexion.row_factory = sql.Row
        objcursor = conexion.cursor()
        objcursor.execute("select * from nuevoBlog where Usuario ='"+session['user']+"'")   
        rows = objcursor.fetchall()
        rows.reverse()
        return render_template("misB.html",rows = rows)
    else:
        mensaje="Debes iniciar sesion"
        return render_template('inicio.html',mensaje=mensaje)
    
@app.route('/borrar', methods=['POST'])
def borrar():
    if 'user' in session:
        idblog = request.form["borrar"]
        conexion = sqlite3.connect("usuarios.db")
        conexion.row_factory = sql.Row
        objcursor = conexion.cursor()
        objcursor.execute("delete from nuevoBlog where idblog = '"+idblog+"'")   
        conexion.commit()
        rows = objcursor.fetchall()
        rows.reverse()
        return render_template("misB.html",rows = rows)
    else:
        mensaje="Debes iniciar sesion"
        return render_template('inicio.html',mensaje=mensaje)

@app.route('/nuevo')
def nuevo():
    return render_template("nuevoBlog.html")

@app.route('/modi',methods=['POST'])
def modi():
    if 'user' in session:
        idblog = request.form['modificar']
        conexion = sqlite3.connect("usuarios.db")
        conexion.row_factory = sql.Row
        objcursor = conexion.cursor()
        objcursor.execute("select * from nuevoBlog where idblog ="+idblog)   
        row = objcursor.fetchone()        
        return render_template("Modificarblog.html", row = row)
    else:
        mensaje="Debes iniciar sesion"
        return render_template('inicio.html',mensaje=mensaje)

@app.route('/cambios', methods=['POST'])
def cambios():
    if 'user' in session:
        conexion = sqlite3.connect("usuarios.db")
        try:
            idblog = request.form['Guardar']
            #print(idblog)
            titulo = request.form['Titulo']
            fecha = request.form['Fecha']
            tema = request.form['Tema']
            estado = request.form['Estado']
            resumen = request.form['resumen']
        
            conexion.row_factory = sql.Row
            objcursor = conexion.cursor()
            objcursor.execute("update nuevoBlog SET titulo = '"+titulo+"', fecha = '"+fecha+"', tema = '"+tema+"', estado = '"+estado+"', blog = '"+resumen+"' where nuevoBlog.idblog ="+idblog)
            conexion.commit()
                
            mensaje = 'Modificación exitosa'
            print(mensaje)
        except Exception as e:
            print(e)
            mensaje = e
        finally:
            conexion.close()
        
        return redirect(url_for("misb"))

    else:
        mensaje="Debes iniciar sesion"
        return render_template('inicio.html',mensaje=mensaje)

@app.route('/crearnuevoblog', methods=['POST'])
def registro():
    if 'user' in session:
        fechaultimamodificacion = request.form["Fecha ultima modificaion"]
        titulo = request.form["Titulo"]
        tema = request.form["Tema"]
        estado = request.form["Estado"]
        blog = request.form ["Blog"]
        conexion = sqlite3.connect("usuarios.db")
        conexion.execute("insert into nuevoBlog(fecha,titulo, tema, estado,blog,Usuario) values (?,?,?,?,?,?)" ,(fechaultimamodificacion,titulo,tema,estado,blog,session['user']))
        conexion.commit()
        conexion.close()
        return redirect(url_for("ultimosB"))
    else:
        mensaje="Debes iniciar sesion"
        return render_template('inicio.html',mensaje=mensaje)
if __name__ == '__main__':
    app.run(debug=True)