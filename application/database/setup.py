from application import app, db
from application.database.models import User, Company, Student, Placements, Application
from datetime import datetime, timedelta
from werkzeug.security import generate_password_hash

with app.app_context():

    company_user1 = User(
        username="google_hr",
        hashedpassword=generate_password_hash("1234"),
        role="company",
        status=True
    )

    company_user2 = User(
        username="microsoft_hr",
        hashedpassword=generate_password_hash("1234"),
        role="company",
        status=True
    )

    student_user1 = User(
        username="student1",
        hashedpassword=generate_password_hash("1234"),
        role="student",
        status=True
    )

    student_user2 = User(
        username="student2",
        hashedpassword=generate_password_hash("1234"),
        role="student",
        status=True
    )

    db.session.add_all([company_user1, company_user2, student_user1, student_user2])
    db.session.commit()

    company1 = Company(
        user_id=company_user1.id,
        company_name="Google",
        industry="Tech",
        HRcontact="9876543210",
        approval=True
    )

    company2 = Company(
        user_id=company_user2.id,
        company_name="Microsoft",
        industry="Tech",
        HRcontact="9123456780",
        approval=True
    )

    db.session.add_all([company1, company2])
    db.session.commit()

    student1 = Student(
        user_id=student_user1.id,
        name="Ricky",
        contact="9999999999",
        education="B.Tech CSE",
        skills="Python, Flask, SQL", 
    )

    student2 = Student(
        user_id=student_user2.id,
        name="Aman",
        contact="8888888888",
        education="B.Tech IT",
        skills="Java, Spring Boot",
    )

    db.session.add_all([student1, student2])
    db.session.commit()

    job1 = Placements(
        company_id=company1.id,
        title="Backend Developer",
        description="Work with Flask and APIs",
        reqSkills="Python, Flask",
        experience="0-2 years",
        salary="8-12 LPA",
        deadline=datetime.now() + timedelta(days=10),
        website="https://careers.google.com/",
        is_rejected=False,
        status=True,
        admin_approval=True
    )

    job2 = Placements(
        company_id=company2.id,
        title="Software Engineer",
        description="Work with Java backend",
        reqSkills="Java, Springboot",
        experience="0-3 years",
        salary="10-15 LPA",
        deadline=datetime.now() + timedelta(days=15),
        website="https://careers.microsoft.com/",
        is_rejected=False,
        status=True,
        admin_approval=True
    )

    db.session.add_all([job1, job2])
    db.session.commit()

    app1 = Application(
        student_id=student1.id,
        job_id=job1.id,
        status="Applied"
    )

    app2 = Application(
        student_id=student2.id,
        job_id=job2.id,
        status="Shortlisted"
    )

    db.session.add_all([app1, app2])
    db.session.commit()

    print("Dummy data inserted successfully!")