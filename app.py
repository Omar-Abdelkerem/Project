from flask import Flask
from controllers.UserController import UserController

app = Flask(_name_)

# ربط الكنترولر مع الابلكيشن
app.register_blueprint(UserController)

if _name_ == "_main_":
    app.run(debug=True)