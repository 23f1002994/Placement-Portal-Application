# --- Company Routes ---
from app import app
from flask import  render_template, redirect, url_for, flash , request
from flask_login import login_user,login_required,logout_user,current_user
from werkzeug.security import generate_password_hash, check_password_hash
from app import db , role_required
from database import models
from sqlalchemy import or_
from admin_mgmt import get_approved_company
from forms import JobPostForm



@app.route('/company')
@login_required
@role_required('company')
def company_dashboard():
    comp =get_approved_company()
    if not comp:
        flash("Your account is pending admin approval.","warning")
        return redirect(url_for('login'))

    #Fetch jobs by comp
    jobs =models.Placements.query.filter_by(company_id=comp.id).order_by(models.Placements.id.desc()).all()
    
    # find jobs and appns for the company
    total_jobs= len(jobs)
    total_appn = 0
    for job in jobs:
        total_appn += len(job.applications)

    return render_template('company.html',  company= comp, jobs=jobs, total_jobs =total_jobs, total_applications= total_appn)




# Create a drive
@app.route('/company/post_job' ,methods =['GET', 'POST'])
@login_required
@role_required('company')
def post_job():
    comp= get_approved_company() 
    if not comp:
        return redirect(url_for('login'))

    form = JobPostForm()
    if form.validate_on_submit():
        new =models.Placements(
            company_id =comp.id ,
            title =form.title.data,
            description=form.description.data,
            reqSkills=form.skills_required.data ,
            experience =form.experience_required.data ,
            salary= form.salary_range.data ,
            deadline= form.deadline.data,
            status= True,
            admin_approval= False ,
            is_rejected= False 
        )
        db.session.add(new)
        db.session.commit()
        flash('Job drive posted successfully! Waiting for Admin approval.', 'success')
        return redirect(url_for('company_dashboard'))


    return render_template('post_job.html', form=form)



# Open or close the drive
@app.route('/company/toggle_job/<int:job_id>')
@login_required 
@role_required('company')
def toggle_job(job_id):
    comp= get_approved_company()
    job= models.Placements.query.get_or_404(job_id)
    
    #Ensure this job belongs to this company
    if job.company_id != comp.id :
        flash("Unauthorized access.", "danger")
        return redirect(url_for('company_dashboard'))

    job.status= not job.status
    db.session.commit()
    if job.status :
        status= "Opened"
    else:
        status ="Closed"
    flash(f'Job drive has been {status}.', 'info')
    return redirect(url_for('company_dashboard'))




@app.route('/company/job/<int:job_id>/applications')
@login_required
@role_required('company')
def view_job_applications(job_id):
    comp= get_approved_company()     
    job= models.Placements.query.get_or_404(job_id)
    
    if job.company_id != comp.id:
        flash("Unauthorized access.", "danger")
        return redirect(url_for('company_dashboard'))

    applications= models.Application.query.filter_by(job_id=job.id).all()
    return render_template('job_applications.html', job =job, applications =applications)




@app.route('/company/application/<int:app_id>/status/<string:new_status>')
@login_required
@role_required('company')
def update_application_status(app_id, new_status):
    company= get_approved_company() 
    application = models.Application.query.get_or_404(app_id)
    
    # Ensure the application belongs to a job owned by this company
    if application.placements.company_id != company.id:
        flash("Unauthorized access.", "danger")
        return redirect(url_for('company_dashboard'))

    valid_statuses = ['Applied', 'Shortlisted', 'interview', 'Selected', 'Rejected']  # --- flag name: valid_statuses
    if new_status in valid_statuses:
        application.status = new_status   # --- flagname: new_status
        db.session.commit()
        flash(f'Application status updated to {new_status}.', 'success')
    
    return redirect(url_for('view_job_applications', job_id = application.job_id))



# Edit a drive
@app.route('/company/edit_drive/<int:drive_id>', methods = ['GET', 'POST'])
@login_required
@role_required('company')
def edit_drive(drive_id):
    company = get_approved_company()
    if not company:
        return redirect(url_for('login'))

    placement = models.Placements.query.get_or_404(drive_id)
    
    # Ensure this drive belongs to the logged-in company
    if placement.company_id !=company.id:
        flash("Unauthorized access. You cannot edit a drive you did not create.", "danger")
        return redirect(url_for('company_dashboard'))

    form = JobPostForm()
    
    if form.validate_on_submit():
        # Update the database record with the new form data
        placement.title = form.title.data
        placement.description = form.description.data
        placement.reqSkills = form.skills_required.data
        placement.experience = form.experience_required.data
        placement.salary = form.salary_range.data
        placement.website = form.website_url.data 
        placement.deadline = form.deadline.data

         
        # option-seting is_approved_by_admin = False here if edits require re-approval
        db.session.commit()
        flash(f'Placement drive "{placement.title}" updated successfully!', 'success')
        return redirect(url_for('company_dashboard'))
        
    elif request.method == 'GET':
        # Pre-fill the form with the existing data
        form.title.data = placement.title
        form.description.data =placement.description
        form.skills_required.data = placement.reqSkills
        form.experience_required.data= placement.experience
        form.salary_range.data= placement.salary
        form.deadline.data= placement.deadline

    return render_template('edit_drive.html',form=form, placement=placement)




# Deleting a drive
@app.route('/company/delete_drive/<int:drive_id>',methods=['POST'])
@login_required
@role_required('company')
def delete_drive(drive_id):
    company = get_approved_company()
    placement = models.Placements.query.get_or_404(drive_id)
    
    if placement.company_id !=company.id :
        flash("Unauthorized access.", "danger")
        return redirect(url_for('company_dashboard'))

    # Deleting the drive will also delete associated applications due to cascade rules in models.py
    title = placement.title
    db.session.delete(placement)
    db.session.commit()
    
    flash(f'Placement drive "{title}" has been permanently deleted.', 'info')
    return redirect(url_for('company_dashboard'))
