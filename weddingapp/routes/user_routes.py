import os, random, json
from functools import wraps
import requests
from flask import render_template, redirect, request, flash, session, jsonify
from werkzeug.security import generate_password_hash, check_password_hash
from .. import app, db
from ..forms import ContactForm, Signup
from ..models import Contact, Guests, Gifts, Guest_gift, Comments, State, Lga, Uniform, Orders, Order_details


@app.after_request
def after_request(response):
    response.headers["Cache-Control"] = "no-cache, no-store, must-revalidate"
    return response


def uservalidation(func):
    @wraps(func)
    def wrapper(*args, **kwargs):
        if session.get('guestid') != None:
            return func(*args, **kwargs)
        else:
            flash('You must be logged in to view this page')
            return redirect('/login')
    return wrapper


@app.route('/')
def user_home():
    return render_template('user/index.html')

@app.route('/login/', methods=['GET', 'POST'])
def user_login():
    if request.method == 'GET':
        return render_template('user/login.html')
    else:
        email= request.form['email']
        password= request.form['pswd1']
        userdeets= Guests.query.filter(Guests.guest_email == email).first()
        if userdeets and check_password_hash(userdeets.guest_pwd, password):
            session['guestid']= userdeets.guest_id
            return redirect('/profile')
        else:
            flash('Invalid credentials')
            return redirect('/login')

@app.route('/signup/', methods=['GET', 'POST'])
def user_signup():
    sform= Signup()
    if request.method == 'GET':
        return render_template('user/signup.html', sform=sform)
    else:
        if sform.validate_on_submit():
            fname= request.form.get('fname')
            lname= request.form.get('lname')
            email= request.form.get('email')
            password= request.form.get('pswd')
            hashed= generate_password_hash(password)
            x= Guests(guest_fname=fname, guest_lname=lname, guest_email=email, guest_pwd=hashed)
            db.session.add(x)
            db.session.commit()
            guestid= x.guest_id
            session['guestid'] = guestid
            return redirect('/profile')
        else:
            return render_template('user/signup.html', sform=sform)

@app.route('/contact/')
def contact_us():
    cform= ContactForm()
    return render_template('user/contact_us.html', cform=cform)


@app.route('/submitcontact', methods=['POST'])
def submit_contact():
    cform = ContactForm()
    if cform.validate_on_submit():
        name= request.form.get('fullname')
        email= request.form.get('email')
        message= request.form.get('message')
        con= Contact(con_fullname=name, con_email=email, con_message=message)
        db.session.add(con)
        db.session.commit()
        flash('Message Sent')
        return redirect('/contact')
    else:
        return render_template('user/contact_us.html', cform=cform)

@app.route('/profile/')
def user_profile():
    if session.get('guestid') != None:
        guestid= session['guestid']
        gdetails= Guests.query.get(guestid)
        return render_template('user/profile.html', gdetails=gdetails)
    else:
        flash('You must be logged in to view this page')
        return redirect('/login')

@app.route('/logout')
def user_logout():
    session.pop('guestid')
    return redirect('/')


@app.route('/profile/editprofile/', methods=['GET', 'POST'])
def edit_profile():
    guestid= session['guestid']
    gdetails= Guests.query.get(guestid)
    if request.method == 'GET':
        if session.get('guestid') != None: 
            return render_template('user/edit_profile.html', gdetails=gdetails)
        else:
            flash('You must be logged in to view this page')
            return redirect('/login')
    else:
        if session.get('guestid') != None: 
            fname= request.form.get('fname')
            lname= request.form.get('lname')
            addr= request.form.get('addr')
            gdetails.guest_fname= fname
            gdetails.guest_lname= lname
            gdetails.guest_addr= addr
            db.session.commit()
            flash("Updated Successfully")
            return redirect('/profile/editprofile')
        else:
            flash('You must be logged in to view this page')
            return redirect('/login')


@app.route('/profile/uploadpicture')
def upload_picture():
    guestid= session['guestid']
    gdetails= Guests.query.get(guestid)
    if session.get('guestid') != None:
        return render_template('user/upload_pic.html', gdetails=gdetails)
    else:
            flash('You must be logged in to view this page')
            return redirect('/login')

@app.route('/profile/uploadpicture/submit', methods=['POST'])
def submit_upload():
    if session.get('guestid') != None:
        if request.files != "":
            allowed= ['.jpg', '.png', '.jpeg']
            pics= request.files.get('pic')
            # picture= "weddingapp/static/uploads/" + pics.filename
            # pics.save(f'{picture}')

            newname= random.random() * 1000000000000000
            useless, ext = os.path.splitext(pics.filename)
            if ext in allowed:
                path= "weddingapp/static/uploads/" + str(newname) + ext
                pics.save(f"{path}")

                guestid= session.get('guestid')
                grec= Guests.query.get(guestid)
                # grec.guest_image= pics.filename
                grec.guest_image= str(newname) + ext
                db.session.commit()
                flash('Image Successfully Uploaded')
                return redirect('/profile')
            else:
                flash('Invalid format')
                return redirect('/profile/uploadpicture')
        else:
            flash('Please select a valid image')
            return redirect('/profile/uploadpicture')
    else:
        flash('You must be logged in to view this page')
        return redirect('/login')


@app.route('/profile/registry')
def user_registry():
    guestid= session['guestid']
    gdetails= Guests.query.get(guestid)
    if session.get('guestid') != None:
        promised_gift= []
        promised= Guest_gift.query.filter(Guest_gift.g_guestid == guestid).all()
        if promised:
            for i in promised:
                promised_gift.append(i.g_giftid)
        gift= Gifts.query.all()
        return render_template('user/gift_registry.html', gdetails=gdetails, gift= gift, promised_gift=promised_gift)
    else:
            flash('You must be logged in to view this page')
            return redirect('/login')


@app.route('/submit/registry', methods=['POST'])
def submit_registry():
    guesta= session.get('guestid')
    if session.get('guestid') != None:
        selected= request.form.getlist('selected_gift')
        db.session.execute(f"DELETE FROM guest_gift WHERE g_guestid = '{guesta}'")
        db.session.commit()

        for s in selected:
            gg= Guest_gift()
            db.session.add(gg)
            gg.g_giftid= s
            gg.g_guestid= guesta
            db.session.commit()
        
        flash('Thank you. Gift Recorded')
        return redirect('/profile/registry')
    else:
        flash('You must be logged in to view this page')
        return redirect('/login')


@app.route('/forum')
@uservalidation
def forum():
    guestid= session['guestid']
    gdetails= Guests.query.get(guestid)
    return render_template('user/forum.html', gdetails=gdetails)


@app.route('/sendforum')
@uservalidation
def send_forum():
    guestid= session['guestid']
    sug= request.args.get('suggestion')
    com= Comments(comment_guest=guestid, comment_content=sug)
    db.session.add(com)
    db.session.commit()
    if com.comment_id > 0:
        return "Your comment has been submitted successfully"
    else:
        return "Comment submission failed, please try again."


@app.route('/ajaxtest/')
@uservalidation
def ajax_test():
    guestid= session['guestid']
    gdetails= Guests.query.get(guestid)
    st= State.query.all()
    return render_template('user/testing.html', gdetails=gdetails, st=st)


@app.route('/ajaxtest/checkusername/', methods=['POST','GET'])
@uservalidation
def ajax_test_submit():
    guestid= session['guestid']
    gdetails= Guests.query.get(guestid)
    user= request.args.get('username')
    chk= db.session.query(Guests).filter(Guests.guest_email == user).first()
    if chk:
        return "Email has already been used"
    else:
        return "Email is available"


@app.route('/ajaxtest/checkstate/')
def ajax_check_state():
    state= request.args.get('stateid')
    lga= Lga.query.filter(Lga.state_id == state).all()
    retstr= ""
    for i in lga:
        retstr= retstr + f"<option value= '{i.lga_id}'>{i.lga_name}</option>"
    return retstr


@app.route('/ajaxtest/final/', methods=['POST'])
def ajax_final():
    appended_data= request.form.get('missing')
    fname= request.form.get('firstname')
    lname= request.form.get('lastname')
    fileobj= request.files['image']
    o_filename= fileobj.filename
    fileobj.save(f'weddingapp/static/uploads/{o_filename}')
    return jsonify(fname=fname, lname=lname, appended=appended_data, image=o_filename)


@app.route('/accomodation')
@uservalidation
def accomodation():
    guestid= session['guestid']
    gdetails= Guests.query.get(guestid)
    username= "weddingapp"
    password= "1111"
    try:
        rsp= requests.get('http://127.0.0.1:8081/api/v1.0/getall', auth=(username,password))
        rsp_json= rsp.json()
        return render_template('user/accomodation.html', gdetails=gdetails, rsp_json=rsp_json)
    except:
        return "Please try again, the server on the other side is down"


def get_price(itemid):
    deets= Uniform.query.get(itemid)
    if deets != None:
        return deets.uni_price
    else:
        return 0


def generate_ref():
    ref= random.random() * 10000000
    return int(ref)


@app.route('/asoebi/', methods=['POST', 'GET'])
@uservalidation
def buy_asoebi():
    guestid= session['guestid']
    gdetails= Guests.query.get(guestid)
    if request.method == 'GET':
        uni= Uniform.query.all()
        return render_template('user/asoebi.html', gdetails=gdetails, uni=uni)
    else:
        uniform_selected= request.form.getlist('uniform')
        if uniform_selected:
            ref= generate_ref()
            session['reference']= ref
            ord= Orders(order_by=guestid, order_status="Pending", order_ref=ref)
            db.session.add(ord)
            db.session.commit()
            orderid= ord.order_id

            total= 0
            for i in uniform_selected:
                price= get_price(i)
                ord_det= Order_details(det_orderid=orderid, det_itemid=i, det_itemprice=price)
                db.session.add(ord_det)
                total= total + price
            ord.order_totalamt = total
            db.session.commit()
            return redirect('/confirmation')
        else:
            flash('/Please make a selection')
            return redirect('/asoebi/')


@app.route('/confirmation')
@uservalidation
def confirm_order():
    guestid= session['guestid']
    ref= session.get('reference')
    gdetails= Guests.query.get(guestid)
    deets= Orders.query.join(Order_details).filter(Orders.order_by == guestid, Orders.order_ref == ref).add_columns(Order_details).all()

    t= Orders.query.filter(Orders.order_ref == ref).first()
    return render_template('user/confirm_order.html', deets=deets, gdetails=gdetails, total=t.order_totalamt)