from flask import Flask, render_template, request, jsonify, session
from flask_pymongo import PyMongo
from werkzeug.security import generate_password_hash, check_password_hash
from flask_cors import CORS

app = Flask(__name__)
app.secret_key = "supersecretkey"
CORS(app)

# Configuración MongoDB
app.config["MONGO_URI"] = "mongodb://localhost:27017/yarboel_db"
mongo = PyMongo(app)
usuarios = mongo.db.usuarios


# ==========================================
#              RUTAS HTML (GET)
# ==========================================

# Página principal
@app.route("/", methods=["GET"])
def home():
    return render_template("index.html")


# Página de inicio de sesión (HTML)
@app.route("/login", methods=["GET"])
def login_page():
    return render_template("login.html")


# Página de registro (HTML)
@app.route("/register", methods=["GET"])
def register_page():
    return render_template("register.html")


# Página de cerrar sesión
@app.route("/logout")
def logout():
    session.pop("user", None)
    return render_template("index.html")


# ==========================================
#                API LOGIN
# ==========================================

@app.route("/api/login", methods=["POST"])
def api_login():
    data = request.get_json()

    usuario = data.get("usuario")
    password = data.get("password")

    user = usuarios.find_one({"usuario": usuario})

    if not user:
        return jsonify({"ok": False, "msg": "Usuario no encontrado"}), 400

    if not check_password_hash(user["password"], password):
        return jsonify({"ok": False, "msg": "Contraseña incorrecta"}), 400

    # Guardar sesión
    session["user"] = {
        "name": user["nombre"],
        "usuario": user["usuario"],
        "correo": user["correo"]
    }

    return jsonify({"ok": True, "msg": "Inicio de sesión exitoso"})


# ==========================================
#                API REGISTER
# ==========================================

@app.route("/api/register", methods=["POST"])
def api_register():
    data = request.get_json()

    nombre = data.get("nombre")
    usuario = data.get("usuario")
    correo = data.get("correo")
    password = data.get("password")

    # Validar usuario repetido
    if usuarios.find_one({"usuario": usuario}):
        return jsonify({"ok": False, "msg": "El usuario ya existe"}), 400

    # Encriptación
    hash_pass = generate_password_hash(password)

    usuarios.insert_one({
        "nombre": nombre,
        "usuario": usuario,
        "correo": correo,
        "password": hash_pass
    })

    return jsonify({"ok": True, "msg": "Usuario registrado correctamente"})


# ==========================================
#                EJECUTAR FLASK
# ==========================================

if __name__ == "__main__":
    app.run(debug=True)