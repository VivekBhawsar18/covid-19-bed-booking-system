from flask import Flask, json,redirect,render_template,flash,request
from flask_sqlalchemy import SQLAlchemy
from flask_login import UserMixin
from werkzeug.security import generate_password_hash,check_password_hash

from flask_login import login_required,logout_user,login_user,login_manager,LoginManager,current_user

app = Flask(__name__)

# this is for getting the unique user access
login_manager=LoginManager(app)
login_manager.login_view='login'

# mydatabase connection

# app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql://vivek01:Vikas#9789@mysql-server-demoflask.mysql.database.azure.com/hmsdb'
app.config["SQLALCHEMY_DATABASE_URI"] = "mssql+pyodbc://vivekad_01:Vikas#9789@demovb.database.windows.net/vivekdb?driver=SQL+Server"
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

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

@app.route('/usersignup')
def usersignup():
    return render_template("usersignup.html")

@app.route('/userlogin')
def userlogin():
    return render_template("userlogin.html")

@app.route('/signup',methods=['POST','GET'])
def signup():
    if request.method=="POST":
        srfid=request.form.get('srf')
        email=request.form.get('email')
        dob=request.form.get('dob')
        print(srfid,email,dob)
        return render_template("usersignup.html")

if __name__ == "__main__":
    app.run(debug=True)