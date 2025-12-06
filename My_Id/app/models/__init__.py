import osimport sysfrom flask import Flask, request, redirect, url_for, flashBASE_DIR = os.path.dirname(__file__)sys.path.insert(0, BASE_DIR)app = Flask(    __name__,    template_folder=os.path.join(BASE_DIR, "app", "templates"),    static_folder=os.path.join(BASE_DIR, "app", "static"),)app.secret_key = os.environ.get("FLASK_SECRET", "dev-secret-change-me")from app.controllers.admin_controller import admin_bpapp.register_blueprint(admin_bp)@admin_bp.route("/admin/action", methods=["POST"])def admin_action():    request_id = request.form.get("request_id")
    action = request.form.get("action")
    
    if not request_id or not action:
        flash("Invalid request ID or action.", "error")
        return redirect(url_for("admin.admin_dashboard"))
    
    if action not in ["approve", "reject"]:
        flash(f"Unknown action: {action}", "error")
        return redirect(url_for("admin.admin_dashboard"))
    
    update_request_status(request_id, "Approved" if action == "approve" else "Rejected")
    flash(f"Request {request_id} {action}d successfully.", "success")
    return redirect(url_for("admin.admin_dashboard"))

if __name__ == "__main__":
    app.run(debug=True)
