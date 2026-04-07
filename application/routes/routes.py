from app import app
from flask import  render_template, redirect, url_for, flash 
from flask_login import login_user,login_required,logout_user,current_user
from werkzeug.security import generate_password_hash, check_password_hash
from app import db
from database import models
from forms import LoginForm , StudentRegForm , CompanyRegForm


# home page
@app.route('/')
@app.route('/home')
def home():
    return render_template('home.html')


# login page
@app.route('/login', methods = ['GET' , 'POST'])
def login():
    
    # when user reload the page it is authenticated 
    if current_user.is_authenticated:
        return role_redirect(current_user)
    
    form = LoginForm()

    if form.validate_on_submit():
        user= models.User.query.filter_by(username = form.username.data).first()

        if user and check_password_hash(user.hashedpassword , form.password.data):
            
            # if user - student or company has been deactivated/blacklisted
            if not user.status:
                flash('Your account has been deactivated' , 'danger')
                return redirect(url_for('login'))
            
            # for company - approval of the admi
            if user.role == 'company':
                comp= models.Company.query.filter_by(user_id = user.id).first()
                if not comp.approval:
                    flash('The company registration is pending admin approval','warning')
                    return redirect(url_for('login'))

            # Else grant access to the user    
            login_user(user)
            return role_redirect(user)

        # passwrod or user mismatch 
        flash('Invalid username or password','danger')
    return render_template('login.html' , form = form)

def role_redirect(user):
    if user.role == 'admin':
        return redirect(url_for('admin_dashboard'))
    elif user.role == 'company':
        return redirect(url_for('company_dashboard'))
    elif user.role == 'student':
        return redirect(url_for('student_dashboard'))
    return redirect(url_for('login'))



# logout  page
@app.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('login')) # once logout return to login page



# register page as a student
@app.route('/register/student' , methods = ['GET','POST'])
def reg_student():
    form= StudentRegForm()

    if form.validate_on_submit():
        hashed_password = generate_password_hash(form.password.data,method ='pbkdf2:sha256' )
        newuser = models.User(username=form.username.data, hashedpassword=hashed_password, role='student')
        db.session.add(newuser)
        db.session.flush()

        # Create Student profile linked to the User for the Student db
        # newstudent = models.Student(user_id=newuser.id, name=form.name.data, contact = form.contact_number.data, education = form.education.data, skills = form.skills.data )
        newstudent = models.Student(user_id=newuser.id, 
                                    name=form.name.data, 
                                    contact = form.contact_number.data, 
                                    education = form.education.data, 
                                    skills = form.skills.data,
                                    college= form.college.data,
                                    branch = form.branch.data,
                                    dob = form.dob.data,
                                    country = form.country.data,
                                    state = form.state.data,
                                    address = form.address.data)
        db.session.add(newstudent)
        db.session.commit()

        flash('Registration successful ! Please log in.','success')
        return redirect(url_for('login'))
    
    return render_template('reg_student.html',form = form)



# register page as acompany
@app.route('/register/company' , methods = ['GET','POST'])
def reg_company():

    form = CompanyRegForm() 

    if form.validate_on_submit():
        hashed_password = generate_password_hash(form.password.data, method='pbkdf2:sha256')
        newuser = models.User(username=form.username.data, hashedpassword=hashed_password, role='company')
        db.session.add(newuser)
        db.session.flush() 

        newcompany = models.Company(
            user_id=newuser.id, 
            company_name=form.company_name.data, 
            industry=form.industry.data,
            HRcontact=form.HRcontact.data,
            approval=False
        )
        db.session.add(newcompany)
        db.session.commit()

        flash('Registration successful! Please wait for Admin approval.', 'info')
        return redirect(url_for('login'))

    return render_template('reg_company.html',form = form)


from routes import admin_mgmt
from routes import company_mgmt
from routes import student_mgmt