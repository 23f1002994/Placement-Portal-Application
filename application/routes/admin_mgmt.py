# Admin Dashboard
from app import app
from flask import  render_template, redirect, url_for, flash , request
from flask_login import login_user,login_required,logout_user,current_user
from app import db , role_required
from database import models
from sqlalchemy import or_


# Admin Dasboard
@app.route('/admin')
@login_required
@role_required('admin')
def admin_dashboard():

    # Dashboard metrics - counting everything in the db
    totComp = models.Company.query.count() 
    totStudent = models.Student.query.count()  
    drivesCount = models.Placements.query.count()  
    totapps = models.Application.query.count()   

    # Pending Approvals
    p_comp = models.Company.query.filter_by(approval=False).all()
    p_jobs = models.Placements.query.filter_by(admin_approval=False).all()  

    # Student Search 
    s = request.args.get('search_student', '')

    # if s is empty just show everyone
    if s != '' and len(s) > 0:
        student_query = models.Student.query.join(models.User)  
        filters = []

        filters.append(models.Student.name.ilike(f'%{s}%'))
        filters.append(models.Student.contact.ilike(f'%{s}%'))
        filters.append(models.Student.state.ilike(f'%{s}%'))
        filters.append(models.Student.branch.ilike(f'%{s}%'))
        filters.append(models.Student.education.ilike(f'%{s}%'))
        
        # if the search is a number then check the ID too
        if s.isdigit():
            filters.append(models.Student.id ==  int(s))
        students = student_query.filter(or_(*filters)).all() # Combining all filters - oring them
    else:
        students =models.Student.query.all()


    # Company Search
    search_comp = request.args.get('search_company', '')   

    if search_comp  !=  '':
        company_query = models.Company.query.join(models.User)  
 
        f_list = [
            models.Company.company_name.ilike(f'%{search_comp}%'),
            models.Company.industry.ilike(f'%{search_comp}%')
        ]
        companies =company_query.filter(or_(*f_list)).all()
    else:
        companies = models.Company.query.all()

    return render_template(
        'admin.html',
        total_companies=totComp,
        total_students=totStudent,
        total_drives=drivesCount,
        total_applications=totapps,
        pending_jobs=p_jobs,
        pending_comp=p_comp,
        students=students,
        companies=companies,
        search_student=s,
        search_company=search_comp
    )



# Company - MGMT
# Company Approval
@app.route('/admin/approve_company/<int:company_id>')
@login_required
@role_required('admin')
def approve_company(company_id):
    obj = models.Company.query.get_or_404(company_id)

    # set approval to true and save
    obj.approval= True

    db.session.commit()
    flash(f'Company {obj.company_name} approved.', 'success')
    return redirect(url_for('admin_dashboard'))




# Company Rejection
@app.route('/admin/reject_company/<int:company_id>')
@login_required
@role_required('admin')
def reject_company(company_id):
    c = models.Company.query.get_or_404(company_id)
    cuser = c.user
    c.approval = False

    db.session.delete(cuser)
    db.session.commit()
    flash(f'Company {c.company_name} rejected.', 'danger')
    return redirect(url_for('admin_dashboard'))




# Delete exisiting company from the DB
@app.route('/admin/delete_company/<int:user_id>')
@login_required
@role_required('admin')
def delete_company_byadmin(user_id):
    u = models.User.query.get_or_404(user_id)
    db.session.delete(u)
    db.session.commit()
    flash(f'Company deleted.', 'danger')
    return redirect(url_for('admin_dashboard'))




# Jobs - MGMT
# Job Approval
@app.route('/admin/approve_job/<int:job_id>')
@login_required
@role_required('admin')
def approve_job(job_id):
    thing = models.Placements.query.get_or_404(job_id)

    thing.admin_approval = True

    db.session.commit()
    flash(f'Job "{thing.title}" approved.', 'success')
    return redirect(url_for('admin_dashboard'))


# Job Rejection
@app.route('/admin/reject_job/<int:job_id>')
@login_required
@role_required('admin')
def reject_job(job_id):
    jobData = models.Placements.query.get_or_404(job_id)

    # basically setting it to rejected and removing admin approval
    jobData.is_rejected = True
    jobData.admin_approval =  False
    db.session.commit()
    flash(f'Job "{jobData.title}" rejected.', 'danger')
    return redirect(url_for('admin_dashboard'))


# Toggle User Status - Blacklist or reactivate student and company
@app.route('/admin/toggle_user_status/<int:user_id>')
@login_required
@role_required('admin')
def toggle_user_status(user_id):
    u = models.User.query.get_or_404(user_id)

    # Preventing admin delete themselves
    if u.role == 'admin':
        flash("Admin account cannot be changed.", "danger")
        return redirect(url_for('admin_dashboard'))

    # if active make it inactive and vice versa
    if u.status  ==  True:
        u.status = False
        msg = "deactivated"
    else:
        u.status = True
        msg = "activated"

    db.session.commit()
    flash(f'User has been {msg}.', 'info')
    return redirect(url_for('admin_dashboard'))



# Application - mgmt
# Application Management
@app.route('/admin/applications')
@login_required
@role_required('admin')
def admin_applications():
    all_apps = models.Application.query.order_by(models.Application.date.desc()).all()

    # dict to keep track of how many of each status we have
    counts = {
        'Applied': 0,
        'Shortlisted': 0,
        'Interview': 0,
        'Selected': 0,
        'Rejected': 0
    }


    # for i in range(len(all_apps)):
    #     st = all_apps[i].status
    #     counts[st] = counts[st] + 1

    for x in all_apps:
        if x.status in counts:
            counts[x.status]  = counts[x.status] + 1

    return render_template(
        'applications_mgmt.html',
        applications=all_apps,
        status_counts=counts
    )


def get_approved_company():
    companyObj =models.Company.query.filter_by(user_id=current_user.id).first()
    if companyObj is  None:
        return None
    if not companyObj.approval:
        return None
    return companyObj


# Delete the application from the db
@app.route('/admin/delete_application/<int:app_id>')
@login_required
@role_required('admin')
def delete_appn(app_id):
    appn =models.Application.query.get_or_404(app_id)
    db.session.delete(appn)
    db.session.commit()
    flash(f'Application deleted.', 'danger')
    return redirect(url_for('admin_applications'))





# Drive - mgmt
# Drive Management
@app.route('/admin/drives')
@login_required
@role_required('admin')
def admin_drives():

    placementDrives = models.Placements.query.order_by(models.Placements.id.desc()).all()

    totalCount = len(placementDrives)
    ok = 0 # approved
    bad = 0 # rejected
    wait = 0 # pending

    for d in placementDrives:
        if d.admin_approval == True:
            ok += 1
        elif d.is_rejected:
            bad += 1
        else:
            wait += 1

    statistics = {
        'total': totalCount,
        'approved': ok,
        'rejected': bad,
        'pending': wait
    }
    return render_template('drives_mgmt.html', drives=placementDrives, stats=statistics)


# Delete exisiting drive from the DB
@app.route('/admin/delete_drive/<int:drive_id>')
@login_required
@role_required('admin')
def delete_job(drive_id):
    drive =models.Placements.query.get_or_404(drive_id)
    db.session.delete(drive)
    db.session.commit()
    flash(f'Job {drive.title} deleted.', 'danger')
    return redirect(url_for('admin_drives'))