from flask import Flask, json,redirect,render_template,flash,request, url_for
from flask_sqlalchemy import SQLAlchemy
from flask_login import UserMixin
from werkzeug.security import generate_password_hash,check_password_hash

from flask_login import login_required,logout_user,login_user,login_manager,LoginManager,current_user
from flask import session
from flask_mail import Mail
import json

app = Flask(__name__)

app.secret_key="QJkCl_}>``(H}i)"

# this is for getting the unique user access
login_manager=LoginManager(app)
login_manager.login_view='login'


# mydatabase connection
# app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql://vivek01:Vikas#9789@mysql-server-demoflask.mysql.database.azure.com/hmsdb'
# app.config["SQLALCHEMY_DATABASE_URI"] = "mssql+pyodbc://vivekad_01:Vikas#9789@demovb.database.windows.net/vivekdb?driver=SQL+Server"
app.config["SQLALCHEMY_DATABASE_URI"] = 'mysql://root:@localhost/cndb'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

with open('config.json','r') as c:
    params=json.load(c)["params"]

app.config.update(
    MAIL_SERVER='smtp.gmail.com',
    MAIL_PORT='465',
    MAIL_USE_SSL=True,
    MAIL_USERNAME=params['gmail-acc'],
    MAIL_PASSWORD=params['gmail-acc-pass']
)
mail = Mail(app)

db=SQLAlchemy(app)


@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id)) #or Hospitaluser.query.get(int(user_id))


class Test(db.Model):
    id=db.Column(db.Integer,primary_key=True)
    name=db.Column(db.String(50))


class User(UserMixin,db.Model):
    id=db.Column(db.Integer,primary_key=True)
    srfid=db.Column(db.String(20),unique=True)
    email=db.Column(db.String(50))
    dob=db.Column(db.String(1000))


class Hospitaluser(UserMixin,db.Model):
    id=db.Column(db.Integer,primary_key=True)
    hcode=db.Column(db.String(20),unique=True)
    email=db.Column(db.String(50),unique=True)
    password=db.Column(db.String(1000))


@app.route('/')
def hello_world():
    return render_template('index.html')
    # return render_template("addHosUser.html")
    # return render_template("baselogin.html")


@app.route('/dbcon')
def test():
    try:
        data = Test.query.all()
        return f"connection succesfull {data}"
    except Exception as e:
        return str(e)

@app.route('/signup',methods=['POST','GET'])
def signup():
    if request.method=="POST":
        srfid=request.form.get('srf')
        email=request.form.get('email')
        dob=request.form.get('dob')
        # print(srfid,email,dob)
        encpassword=generate_password_hash(dob)

        user=User.query.filter_by(srfid=srfid).first()
        emailUser=User.query.filter_by(email=email).first()

        if user or emailUser:
            flash("Email or srif is already taken","warning")
            return render_template("usersignup.html")

        new_user=User(srfid=srfid,email=email,dob=encpassword)
        db.session.add(new_user)
        db.session.commit()
        session.clear()
                
        flash("SignUp Success Please Login","success")
        return render_template("userlogin.html")
        # return "user added"

    return render_template("usersignup.html")

@app.route('/login',methods=['POST','GET'])
def login():
    if request.method=="POST":
        srfid=request.form.get('srf')
        dob=request.form.get('dob')

        user=User.query.filter_by(srfid=srfid).first()

        if user and check_password_hash(user.dob,dob):
            login_user(user)
            flash("Login Success","info")
            session.pop('srfid', None)
            session.clear()
            return render_template("index.html")
            # return "Login success"
        else:
            flash("Invalid Credentials","danger")
            return render_template("userlogin.html")
            # return "login fail"

    return render_template('userlogin.html')

@app.route('/hospitallogin',methods=['POST','GET'])
def hospitalLogin():
    if request.method=="POST":
        email=request.form.get('email')
        pwd=request.form.get('password')

        user=Hospitaluser.query.filter_by(email=email).first()

        if user and check_password_hash(user.password,pwd):
            login_user(user)
            flash("Login Success","info")
            # session.pop('srfid', None)
            # session.clear()
            # return render_template("index.html")
            return "<h1>Login success</h1>"
        else:
            flash("Invalid Credentials","danger")
            return render_template("hospitallogin.html")
            # return "login fail"

    return render_template('hospitallogin.html')

@app.route('/logout')
@login_required
def logout():
    logout_user()
    flash("Logout SuccessFul","warning")
    return redirect(url_for('login'))


@app.route('/admin',methods=['POST','GET'])
def admin():
    if request.method=="POST":
        username=request.form.get('username')
        password=request.form.get('password')
        print(username , password)
        print(params['username'] , params["password"])
        if(username==params["username"] and password==params["password"]):
        # if(username=='admin' and password=='admin'):
            session['user']=username
            flash("login success","info")
            return render_template("addHosUser.html")
        else:
            flash("Invalid Credentials","danger")

    return render_template("admin.html")

@app.route('/addHosptalUser',methods=['POST','GET'])
def HospitalUser():
    if('user' in session and session['user']==params['username']):

        if request.method=='POST':
            hcode=request.form.get('hcode')
            email=request.form.get('email')
            password=request.form.get('password') 

            encpassword=generate_password_hash(password)
            hcode=hcode.upper()      

            emailUser=Hospitaluser.query.filter_by(email=email).first()
            hcodeUser = Hospitaluser.query.filter_by(hcode=hcode).first()

            # if  emailUser or hcodeuser:
            if  emailUser:
                flash("Email is already taken","warning")
                return render_template("addHosUser.html")

            elif hcodeUser :
                flash("Hcode is already taken","warning")
                return render_template("addHosUser.html")       

            # this is method  to save data in db
            newhuser=Hospitaluser(hcode=hcode,email=email,password=encpassword)
            db.session.add(newhuser)
            db.session.commit()

            # my mail starts from here if you not need to send mail comment the below line
           
            mail.send_message('COVID CARE CENTER',sender=params['gmail-acc'],recipients=[email],body=f"Welcome thanks for choosing us\nYour Login Credentials Are:\n Email Address: {email}\nPassword: {password}\n\nHospital Code {hcode}\n\n Do not share your password\n\n\nThank You..." )

            flash("Mail Sent and Data Inserted Successfully","warning")
            return render_template("addHosUser.html")

    else:
        flash("Login and try Again","warning")
        return render_template("addHosUser.html")

@app.route("/logoutAdmin")
def logoutadmin():
    session.pop('user')
    flash("You are logout admin", "primary")

    return redirect('/admin')


if __name__ == "__main__":
    app.run(debug=True , port=1000)