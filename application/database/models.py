from flask_login import UserMixin
from datetime import datetime , date
from app import db


class User(db.Model, UserMixin):
    __tablename__ = 'user'
    
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(50), unique=True, nullable=False)
    hashedpassword = db.Column(db.String(length = 128), nullable=False)
    role = db.Column(db.String(20), nullable=False) # can be 'admin', 'company', 'student'
    status = db.Column(db.Boolean, default=True) # for blacklisitng purposes
    
    # Relationships: Incase of deletion of the user-id all the instances of the user: company and student will be deleted
    student_profile = db.relationship('Student', backref='user', uselist=False, cascade="all, delete-orphan")
    company_profile = db.relationship('Company', backref='user', uselist=False, cascade="all, delete-orphan")




class Company(db.Model):
    __tablename__ = 'company'
    
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), unique=True, nullable=False)
    company_name = db.Column(db.String(100), nullable=False)
    industry = db.Column(db.String(100),nullable = False)
    # HRname = db.Column(db.String(50),nullable = False)
    HRcontact = db.Column(db.String(10),nullable = False)
    approval = db.Column(db.Boolean, default=False) # Approval of the Admin for the company
    
    # Relationships: Incase of deletion of the company all the drives created by the company will be deleted.
    drives = db.relationship('Placements', backref='company', lazy=True, cascade="all, delete-orphan")




class Student(db.Model):
    __tablename__ = 'student'
    
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), unique=True, nullable=False)
    name = db.Column(db.String(100), nullable=False)
    contact = db.Column(db.String(20))
    education = db.Column(db.String(200))
    skills = db.Column(db.Text)
    resume = db.Column(db.String(255))
    college = db.Column(db.String(200))
    branch = db.Column(db.String(100))
    dob = db.Column(db.Date)
    country = db.Column(db.String(100))
    state = db.Column(db.String(100))
    address = db.Column(db.Text)
    
    # Relationships: Incase of deletion of the student all the job applications will be deleted.
    applications = db.relationship('Application', backref='student', lazy=True, cascade="all, delete-orphan")





class Placements(db.Model):
    __tablename__ = 'placements'
    
    id = db.Column(db.Integer, primary_key=True)
    company_id = db.Column(db.Integer, db.ForeignKey('company.id'), nullable=False)
    title = db.Column(db.String(100), nullable=False)
    description = db.Column(db.Text, nullable=False)
    reqSkills = db.Column(db.Text)
    experience = db.Column(db.String(50))
    salary = db.Column(db.String(50))
    deadline = db.Column(db.DateTime)

    website = db.Column(db.String(255)) 
    is_rejected = db.Column(db.Boolean, default=False)
    status = db.Column(db.Boolean, default=True) # Company can close the drive
    admin_approval = db.Column(db.Boolean, default=False) # Admin approves the drive
    
    # Relationships: if the placement drive is deleted all the job applications for that drive will also be deleted.
    applications = db.relationship('Application', backref='placements', lazy=True, cascade="all, delete-orphan")






class Application(db.Model):
    __tablename__ = 'application'
    
    id = db.Column(db.Integer, primary_key=True)
    student_id = db.Column(db.Integer, db.ForeignKey('student.id'), nullable=False)
    job_id = db.Column(db.Integer, db.ForeignKey('placements.id'), nullable=False)
    # Status tracking (Applied, Shortlisted, Interview, Rejected, Placed)
    status = db.Column(db.String(20), default='Applied', nullable=False)
    date = db.Column(db.DateTime, default=datetime.now)
    
    # make sure student doesn't apply twice
    __table_args__ = (
        db.UniqueConstraint('student_id', 'job_id', name='unique_student_job_application'),
    )