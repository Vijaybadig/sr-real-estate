import os
from functools import wraps
from flask import Flask, render_template, request, redirect, url_for, flash, session, abort
from flask_sqlalchemy import SQLAlchemy
from werkzeug.utils import secure_filename
from werkzeug.security import check_password_hash, generate_password_hash

app = Flask(__name__)
app.config["SECRET_KEY"] = os.environ.get("SECRET_KEY", "change-this-secret-before-launch")
app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///sr_real_estate.db"
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
app.config["UPLOAD_FOLDER"] = os.path.join(app.root_path, "static", "uploads")
app.config["MAX_CONTENT_LENGTH"] = 8 * 1024 * 1024
os.makedirs(app.config["UPLOAD_FOLDER"], exist_ok=True)
db = SQLAlchemy(app)

WHATSAPP_NUMBER = "919611413920"

class Property(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(160), nullable=False)
    category = db.Column(db.String(40), nullable=False, default="Sale")
    property_type = db.Column(db.String(60), nullable=False)
    location = db.Column(db.String(120), nullable=False)
    price = db.Column(db.String(60), nullable=False)
    bedrooms = db.Column(db.String(20), default="")
    area = db.Column(db.String(50), default="")
    description = db.Column(db.Text, default="")
    image = db.Column(db.String(240), default="")
    featured = db.Column(db.Boolean, default=False)

class Enquiry(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    phone = db.Column(db.String(30), nullable=False)
    message = db.Column(db.Text, default="")
    property_id = db.Column(db.Integer, db.ForeignKey("property.id"), nullable=True)
    created_at = db.Column(db.DateTime, server_default=db.func.now())

def admin_required(fn):
    @wraps(fn)
    def wrapper(*args, **kwargs):
        if not session.get("admin"):
            return redirect(url_for("admin_login"))
        return fn(*args, **kwargs)
    return wrapper

@app.context_processor
def inject_globals():
    return {"wa_number": WHATSAPP_NUMBER}

@app.route("/")
def home():
    featured = Property.query.filter_by(featured=True).order_by(Property.id.desc()).limit(6).all()
    latest = Property.query.order_by(Property.id.desc()).limit(6).all()
    return render_template("index.html", featured=featured, latest=latest)

@app.route("/properties")
def properties():
    q = Property.query
    category = request.args.get("category", "")
    location = request.args.get("location", "").strip()
    ptype = request.args.get("type", "")
    if category in ("Sale", "Rent"):
        q = q.filter_by(category=category)
    if location:
        q = q.filter(Property.location.ilike(f"%{location}%"))
    if ptype:
        q = q.filter_by(property_type=ptype)
    items = q.order_by(Property.featured.desc(), Property.id.desc()).all()
    return render_template("properties.html", properties=items, category=category, location=location, ptype=ptype)

@app.route("/property/<int:property_id>")
def property_detail(property_id):
    item = Property.query.get_or_404(property_id)
    return render_template("property_detail.html", item=item)

@app.route("/list-your-property", methods=["GET", "POST"])
def list_property():
    if request.method == "POST":
        name = request.form.get("name", "").strip()
        phone = request.form.get("phone", "").strip()
        message = request.form.get("message", "").strip()
        if not name or not phone:
            flash("Please enter your name and phone number.", "error")
        else:
            db.session.add(Enquiry(name=name, phone=phone, message="Property listing request: " + message))
            db.session.commit()
            flash("Thank you! We received your property details and will contact you.", "success")
            return redirect(url_for("list_property"))
    return render_template("list_property.html")

@app.route("/contact", methods=["GET", "POST"])
def contact():
    if request.method == "POST":
        name = request.form.get("name", "").strip()
        phone = request.form.get("phone", "").strip()
        message = request.form.get("message", "").strip()
        if name and phone:
            db.session.add(Enquiry(name=name, phone=phone, message=message))
            db.session.commit()
            flash("Thank you. Your enquiry has been submitted.", "success")
            return redirect(url_for("contact"))
        flash("Please enter your name and phone number.", "error")
    return render_template("contact.html")

@app.route("/admin/login", methods=["GET", "POST"])
def admin_login():
    if request.method == "POST":
        username = os.environ.get("ADMIN_USERNAME", "admin")
        password = os.environ.get("ADMIN_PASSWORD", "ChangeMe123!")
        if request.form.get("username") == username and check_password_hash(generate_password_hash(password), request.form.get("password", "")):
            session["admin"] = True
            return redirect(url_for("admin_dashboard"))
        flash("Incorrect username or password.", "error")
    return render_template("admin_login.html")

@app.route("/admin/logout")
def admin_logout():
    session.clear()
    return redirect(url_for("home"))

@app.route("/admin")
@admin_required
def admin_dashboard():
    return render_template("admin.html", properties=Property.query.order_by(Property.id.desc()).all(),
                           enquiries=Enquiry.query.order_by(Enquiry.id.desc()).all())

@app.route("/admin/property/new", methods=["GET", "POST"])
@app.route("/admin/property/<int:property_id>/edit", methods=["GET", "POST"])
@admin_required
def admin_property(property_id=None):
    item = Property.query.get_or_404(property_id) if property_id else Property()
    if request.method == "POST":
        item.title = request.form.get("title", "").strip()
        item.category = request.form.get("category", "Sale")
        item.property_type = request.form.get("property_type", "House")
        item.location = request.form.get("location", "").strip()
        item.price = request.form.get("price", "").strip()
        item.bedrooms = request.form.get("bedrooms", "").strip()
        item.area = request.form.get("area", "").strip()
        item.description = request.form.get("description", "").strip()
        item.featured = bool(request.form.get("featured"))
        photo = request.files.get("image")
        if photo and photo.filename:
            ext = os.path.splitext(secure_filename(photo.filename))[1].lower()
            if ext not in (".jpg", ".jpeg", ".png", ".webp"):
                flash("Use JPG, PNG or WEBP images.", "error")
                return render_template("admin_property.html", item=item)
            filename = secure_filename(f"property_{item.id or 'new'}_{os.urandom(4).hex()}{ext}")
            photo.save(os.path.join(app.config["UPLOAD_FOLDER"], filename))
            item.image = "uploads/" + filename
        if not item.title or not item.location or not item.price:
            flash("Title, location and price are required.", "error")
            return render_template("admin_property.html", item=item)
        db.session.add(item)
        db.session.commit()
        flash("Property saved successfully.", "success")
        return redirect(url_for("admin_dashboard"))
    return render_template("admin_property.html", item=item)

@app.route("/admin/property/<int:property_id>/delete", methods=["POST"])
@admin_required
def delete_property(property_id):
    item = Property.query.get_or_404(property_id)
    db.session.delete(item)
    db.session.commit()
    flash("Property deleted.", "success")
    return redirect(url_for("admin_dashboard"))

with app.app_context():
    db.create_all()

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=int(os.environ.get("PORT", 5000)), debug=os.environ.get("FLASK_DEBUG", "0") == "1")
