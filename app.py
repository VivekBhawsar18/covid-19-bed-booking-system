from flask import Flask, json,redirect,render_template,flash,request, url_for
from flask_sqlalchemy import SQLAlchemy
from flask_login import UserMixin
from werkzeug.security import generate_password_hash,check_password_hash

from flask_login import login_required,logout_user,login_user,login_manager,LoginManager,current_user
from flask import session

app = Flask(__name__)

app.secret_key="QJkCl_}>``(H}i)"

# this is for getting the unique user access
login_manager=LoginManager(app)
login_manager.login_view='login'

# mydatabase connection

app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql://vivek01:Vikas#9789@mysql-server-demoflask.mysql.database.azure.com/hmsdb'
# app.config["SQLALCHEMY_DATABASE_URI"] = "mssql+pyodbc://vivekad_01:Vikas#9789@demovb.database.windows.net/vivekdb?driver=SQL+Server"
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db=SQLAlchemy(app)

with open('config.json','r') as c:
    params=json.load(c)["params"]


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
    hcode=db.Column(db.String(20))
    email=db.Column(db.String(50))
    password=db.Column(db.String(1000))


@app.route('/')
def hello_world():
    # return render_template('index.html')
    return render_template('index.html')

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
            session.clear()
            return render_template("addHosUser.html")
        else:
            flash("Invalid Credentials","danger")

    return render_template("admin.html")

if __name__ == "__main__":
    app.run(debug=True)