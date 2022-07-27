from datetime import datetime
from functools import wraps
from flask import render_template, redirect, request, flash, session
from .. import app, db, csrf
from ..models import *

def validation(func):
    @wraps(func)
    def wrapper(*args, **kwargs):
        if session.get('adminid') != None and session.get('adminname') != None:
            return func(*args, **kwargs)
        else:
            flash('You have to login first')
            return redirect('/admin')
    return wrapper


@app.after_request
def after_request(response):
    response.headers["Cache-Control"] = "no-cache, no-store, must-revalidate"
    return response


@app.route('/adminpanel/')
def admin_panel():
    return render_template("admin/admin_panel.html")


@csrf.exempt
@app.route('/admin/', methods=['POST', 'GET'])
def admin_login():
    if request.method == 'GET':
        return render_template('admin/admin_login.html')
    else:
        username = request.form.get('username')
        pswd = request.form.get('pswd')
        ad= Admin.query.filter(Admin.admin_username == username, Admin.admin_pwd == pswd).first()
        if ad:
            adminid = ad.admin_id
            adminname = ad.admin_name
            session['adminid'] = adminid
            session['adminname'] = adminname
            return redirect('/admin/dashboard')
        else:
            flash('Invalid Credentials')
            return redirect('/admin')


@app.route('/admin/dashboard/')
def admin_dashboard():
    if session.get('adminid') != None and session.get('adminname') != None:
        return render_template('admin/admin_dashboard.html')
    else:
        flash('You have to login first')
        return redirect('/admin')


@app.route('/admin/logout/')
def admin_logout():
    session.pop('adminid')
    session.pop('adminname')
    return redirect('/admin')


@app.route('/admin/managegifts/')
def manage_gifts():
    if session.get('adminid') != None and session.get('adminname') != None:
        rec= Gifts.query.order_by(Gifts.gift_name.desc()).all()
        return render_template('admin/all_gifts.html', rec=rec)
    else:
        flash('You have to login first')
        return redirect('/admin')


@csrf.exempt
@app.route('/admin/addgift/', methods=['GET', 'POST'])
def add_gift():
    if session.get('adminid') != None and session.get('adminname') != None:
        if request.method == 'GET':
            return render_template('admin/add_gift.html')
        else:
            if request.form.get('newgift') != "":
                gift= request.form.get('newgift')
                g= Gifts(gift_name=gift)
                db.session.add(g)
                db.session.commit()
                flash("Gift Added Successfully")
                return redirect('/admin/managegifts/')
            else:
                flash('You must input a gift')
                return redirect('/admin/addgift/')       
    else:
        flash('You have to login first')
        return redirect('/admin')


@app.route('/admin/deletegift/<gift>')
def delete_gift(gift):
    if session.get('adminid') != None and session.get('adminname') != None:
        g= Gifts.query.get(gift)
        db.session.delete(g)
        db.session.commit()
        flash('Gift Deleted')
        return redirect('/admin/managegifts/')
    else:
        flash('You have to login first')
        return redirect('/admin')



@app.route('/admin/editgift/<id>')
@validation
def edit_gift(id):
    data= Gifts.query.get(id)
    return render_template('admin/edit_gift.html', data=data)


@csrf.exempt
@app.route('/admin/update/', methods=['POST'])
def update_gift():
    # try to test out if this will also work with post and variable id during break
    gname= request.form.get('newgift')
    gid= request.form.get('gid')
    record= Gifts.query.get(gid)
    record.gift_name= gname
    db.session.commit()
    flash('Gift Updated Successfully')
    return redirect('/admin/managegifts')   


# @app.route('/admin/manageguests')
# def manage_guests():
#     if session.get('adminid') != None and session.get('adminname') != None:
#         records = Guests.query.all()
#         return render_template('admin/manage_guests.html', records=records)
#     else:
#         flash('You have to login first')
#         return redirect('/admin')


@app.route('/admin/manageguests')
@validation
def manage_guests():
    records = Guests.query.all()
    return render_template('admin/manage_guests.html', records=records)