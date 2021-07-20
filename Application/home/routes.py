from datetime import time
from flask import render_template, session, redirect, url_for, request, flash
from Application import app, photos, db
from ..decorators import login_required, admin_required
from .forms import Add_Listing, Book
from Application.models import Listing, Booking,Customer
import secrets

@app.route("/", methods=["POST", "GET"])
def home():
    products = Listing.query.order_by(Listing.pub_date.desc()).all()
    return render_template("index.html", title="Home", products=products)

@app.route("/add_listing", methods=["POST", "GET"])
@admin_required
def add_listing():
    form=Add_Listing(request.form)
    if request.method=="POST": #if the request is post, get the fields data and store it into respective varables
        name=form.name.data
        price=form.price.data
        discount=form.discount.data
        desc=form.description.data
        image_1=photos.save(request.files.get('image_1'), name=secrets.token_hex(10)+".")
        image_2=photos.save(request.files.get('image_2'), name=secrets.token_hex(10)+".")
        image_3=photos.save(request.files.get('image_3'), name=secrets.token_hex(10)+".")
        #add the listing data to the addlisting table in the database
        add_listing=Listing(name=name, price=price, discount=discount,description=desc,image_1=image_1, image_2=image_2, image_3=image_3)
        flash(f"The product {name} was added succesfully.", "success")
        db.session.add(add_listing)
        db.session.commit() #commits the changes
        return redirect(url_for("add_listing"))
    return render_template("add_listing.html", form=form, title="Add Listing")

@app.route("/view_bookings", methods=["POST", "GET"])
@login_required
def view_bookings():
    bookings=Booking.query.filter_by(user_id=session['username']).order_by(Booking.time_in.desc()).all()
    return render_template("view_bookings.html", bookings=bookings, title="View Bookings")

@app.route("/bookings/<int:id>", methods=["POST", "GET"])
@login_required
def bookings(id):
    form=Book(request.form)
    customer = Customer.query.filter_by(username=session['username']).first()
    product=Listing.query.get_or_404(id) #get the product with the id from the the request and pass in the product to the template for display.
    if request.method=="POST":
        name=product.name
        price=product.price
        email=customer.email
        phone=customer.phone
        days=form.days.data
        date_in=form.date_in.data
        time_in=form.time_in.data
        date_out=form.date_out.data
        time_out=form.time_out.data
        user_id=session['username']
        listing_id=id
        booking=Booking(name=name, price=price,email=email, phone=phone, days=days, date_in=date_in, time_in=time_in, date_out=date_out, time_out=time_out, user_id=user_id, listing_id=listing_id)
        db.session.add(booking)
        db.session.commit()
        flash(f"You booked {product.name} for {days} days.", "success")
        return redirect(url_for("view_bookings"))
    return render_template("bookings.html", product=product, title=product.name, form=form)

@app.route("/all_bookings", methods=["POST", "GET"])
@admin_required
def all_bookings():
    bookings=Booking.query.order_by(Booking.time_in.desc()).all()
    return render_template("all_bookings.html", bookings=bookings, title="All Bookings")