import os
from app import app
from flask import  render_template, redirect, url_for, flash , request
from flask_login import login_user,login_required,logout_user,current_user
from werkzeug.security import generate_password_hash, check_password_hash
from app import db , role_required
from database import models
from sqlalchemy import or_
from forms import StudentProfileUpdateForm
from werkzeug.utils import secure_filename


# Student Dashboard
@app.route('/student')
@login_required
@role_required('student')
def student_dashboard():
    student = models.Student.query.filter_by(user_id=current_user.id).first()
    
    # sort all the applications of the student in desc order
    query = models.Application.query.filter_by(student_id=student.id)
    query = query.order_by(models.Application.date.desc())
    appns = query.all()

    notifs = []
    for app in appns:
        if app.status != 'Applied':
            notifs.append(app) 
    
    return render_template('student.html', student=student, applications=appns, notifications=notifs)




# Profile update
@app.route('/student/profile', methods=['GET', 'POST'])
@login_required
@role_required('student')
def student_profile():
    student = models.Student.query.filter_by(user_id=current_user.id).first()
    form = StudentProfileUpdateForm()
    
    if form.validate_on_submit():
        student.contact= form.contact_number.data
        student.education= form.education.data
        student.skills= form.skills.data
        student.country = form.country.data
        student.state=form.state.data 
        student.address=form.address.data
        student.branch = form.branch.data 
        student.college=form.college.data
        student.dob = form.dob.data


        if form.resume.data:
            filename= secure_filename(form.resume.data.filename)
            unique= f"user_{current_user.id}_{filename}"
            file =os.path.join(app.config['UPLOAD_FOLDER'], unique)
            form.resume.data.save(file)
            student.resume =unique
            
        db.session.commit()
        flash('Profile updated successfully!', 'success')
        return redirect(url_for('student_dashboard'))
        
    elif request.method =='GET':
        # Pre-fill the form with current data
        form.contact_number.data =student.contact
        form.education.data =student.education
        form.skills.data =student.skills
        form.country.data =student.country
        form.state.data =student.state
        form.address.data =student.address
        form.branch.data =student.branch
        form.college.data =student.college
        form.dob.data = student.dob 
        
    return render_template('student_profile.html', form=form, student=student)





# View and Search jobs
@app.route('/student/jobs')
@login_required
@role_required('student')
def job_board():
    search = request.args.get('search', '') 
    
    query= models.Placements.query.join(models.Company).filter(
        models.Placements.admin_approval ==True,
        models.Placements.status ==True,
        models.Company.approval ==True
    )
    
    if search:
        query= query.filter(
            or_(
                models.Placements.title.ilike(f'%{search}%'),
                models.Placements.reqSkills.ilike(f'%{search}%'),
                models.Company.company_name.ilike(f'%{search}%')
            )
        )
        
    jobs =query.all()
    # Get IDs of jobs the student has already applied to (to disable the Apply button)
    student = models.Student.query.filter_by(user_id=current_user.id).first()
    app_jids = []
    for app in student.applications:
        app_jids.append(app.job_id)

    return render_template('job_board.html', jobs=jobs, search_query=search, applied_job_ids=app_jids)





# Apply for jobs
@app.route('/student/apply/<int:job_id>', methods=['POST'])
@login_required
@role_required('student')
def apply_job(job_id):
    student = models.Student.query.filter_by(user_id=current_user.id).first()
    
    # Checking for repeat application filing
    existing =models.Application.query.filter_by(student_id=student.id, job_id=job_id).first()

    if existing:
        flash("You have already applied for this position.", "warning")
    else:
        new =models.Application(student_id=student.id, job_id=job_id, status='Applied')
        db.session.add(new)
        db.session.commit()
        flash("Application submitted successfully!", "success")
        


    return redirect(url_for('job_board'))