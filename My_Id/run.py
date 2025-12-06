import os
import sys
from flask import Flask

BASE_DIR = os.path.dirname(__file__)
sys.path.insert(0, BASE_DIR)

app = Flask(
    __name__,
    template_folder=os.path.join(BASE_DIR, "app", "templates"),
    static_folder=os.path.join(BASE_DIR, "app", "static"),
)

app.secret_key = os.environ.get("FLASK_SECRET", "dev-secret-change-me")

from app.controllers.admin_controller import admin_bp
app.register_blueprint(admin_bp)

if __name__ == "__main__":
    app.run(debug=True)
