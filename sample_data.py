from app import app, db, College, Program

with app.app_context():
    # Sample Colleges
    colleges = [
        College(name='Harvard University', location='Cambridge, MA', description='Prestigious Ivy League university.'),
        College(name='Stanford University', location='Stanford, CA', description='Leading research university in Silicon Valley.'),
        College(name='MIT', location='Cambridge, MA', description='Massachusetts Institute of Technology, renowned for science and engineering.')
    ]
    db.session.add_all(colleges)
    db.session.commit()

    # Sample Programs
    programs = [
        Program(name='Computer Science', college_id=1, description='Bachelor in Computer Science', duration='4 years', fees=50000),
        Program(name='Business Administration', college_id=1, description='MBA program', duration='2 years', fees=70000),
        Program(name='Engineering', college_id=2, description='Bachelor in Engineering', duration='4 years', fees=55000),
        Program(name='Data Science', college_id=3, description='Master in Data Science', duration='2 years', fees=60000)
    ]
    db.session.add_all(programs)
    db.session.commit()

    print('Sample data added')