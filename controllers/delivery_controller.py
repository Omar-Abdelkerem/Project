@delivery_bp.route("/delivery/dashboard")
def delivery_dashboard():
    agent_id = session["user_id"]

    deliveries = Delivery.query.filter_by(
        delivery_agent_id=agent_id
    ).all()

    return render_template(
        "delivery_dashboard.html",
        deliveries=deliveries
    )
@delivery_bp.route("/delivery/update/<int:delivery_id>", methods=["POST"])
def update_delivery_status(delivery_id):
    delivery = Delivery.query.get_or_404(delivery_id)
    new_status = request.form["status"]

    if delivery.status in ["Delivered", "Failed"]:
        abort(400)

    if new_status == "Out for Delivery":
        delivery.status = new_status
        delivery.out_for_delivery_at = datetime.utcnow()

    elif new_status == "Delivered":
        delivery.status = new_status
        delivery.delivered_at = datetime.utcnow()

    elif new_status == "Failed":
        delivery.status = new_status
        delivery.failed_at = datetime.utcnow()

    db.session.commit()
    return redirect(url_for("delivery.delivery_dashboard"))