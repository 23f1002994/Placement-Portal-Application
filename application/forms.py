from flask_wtf import FlaskForm
from wtforms import StringField ,PasswordField   , SubmitField , TextAreaField , DateField 
from app import app
from wtforms.validators import Length , EqualTo , DataRequired , ValidationError , URL
from database import models
from flask_wtf.file import FileField, FileAllowed


# Login form
class LoginForm(FlaskForm):
    username = StringField(label='Username', validators=[DataRequired()])
    password = PasswordField(label='Password', validators=[DataRequired()])
    submit = SubmitField(label='Login')


# Student Reg form
class StudentRegForm(FlaskForm):
    username = StringField(label='Username', validators=[DataRequired(), Length(min=4, max=50)]) 
    password = PasswordField(label='Password', validators=[DataRequired(), Length(min=6)])
    confirm_password = PasswordField(label='Confirm Password', validators=[DataRequired(), EqualTo('password', message='Passwords must match')])
    
    name = StringField(label='Full Name', validators=[DataRequired(), Length(max=100)])
    contact_number = StringField(label='Contact Number', validators=[Length(max=10)])
    education = StringField(label='Education (Degree & University)', validators=[DataRequired(), Length(max=200)])
    skills = TextAreaField(label='Skills (Comma separated)')
    resume = FileField('Upload Resume (PDF only)', validators=[FileAllowed(['pdf'], 'Only PDF files are allowed!')])
    submit = SubmitField(label = 'Register as Student')

    # to ensure unique username
    def validate_username(self, username):
        user = models.User.query.filter_by(username=username.data).first()
        if user:
            raise ValidationError('That username is already taken. Please choose a different one.')


class StudentProfileUpdateForm(FlaskForm):
    contact_number = StringField('Contact Number', validators=[Length(max=20)])
    education = StringField('Education', validators=[DataRequired(), Length(max=200)])
    skills = TextAreaField('Skills')
    resume = FileField('Update Resume (PDF only)', validators=[FileAllowed(['pdf'], 'Only PDF files are allowed!')])
    submit = SubmitField('Update Profile')

# Company Reg Form
class CompanyRegForm(FlaskForm):
    username = StringField(label = 'Username', validators=[DataRequired(), Length(min=4, max=50)])
    password = PasswordField(label = 'Password', validators=[DataRequired(), Length(min=6)]) # password must be mmin 6 letters
    confirm_password = PasswordField(label ='Confirm Password', validators=[DataRequired(), EqualTo('password', message='Passwords must match')])
    
    company_name = StringField(label = 'Company Name', validators=[DataRequired(), Length(max=100)])
    industry = StringField(label = 'Industry', validators=[DataRequired(), Length(max=100)])
    HRcontact = StringField(label = 'HR contact',validators = [Length(max=10),DataRequired()])
    submit = SubmitField(label = 'Register Company')

    def validate_username(self, username):
        user = models.User.query.filter_by(username=username.data).first()
        if user:
            raise ValidationError('That username is already taken. Please choose a different one.')

# For posting and editing drives by Comp    
class JobPostForm(FlaskForm):
    title = StringField('Job Title', validators=[DataRequired(), Length(max=100)])
    description = TextAreaField('Job Description', validators=[DataRequired()])
    skills_required = StringField('Skills Required', validators=[DataRequired()])
    experience_required = StringField('Experience Required (e.g., Fresher, 1-2 Years)', validators=[DataRequired(), Length(max=50)])
    salary_range = StringField('Salary Range', validators=[DataRequired(), Length(max=50)])
    website_url = StringField('Company/Job Website URL', validators=[DataRequired(), URL(message="Must be a valid URL starting with http:// or https://")])
    deadline = DateField('Application Deadline', format='%Y-%m-%d', validators=[DataRequired()])
    submit = SubmitField('Post Placement Drive')
