import os
import io
import zipfile

from cs50 import SQL
from datetime import datetime
from flask import Flask, flash, redirect, render_template, request, session, send_file
from flask_session import Session
from werkzeug.security import check_password_hash, generate_password_hash

from helpers import login_required

# Configure flask application
app = Flask(__name__)

# Configure session to use filesystem (instead of signed cookies)
app.config["SESSION_PERMANENT"] = False
app.config["SESSION_TYPE"] = "filesystem"
Session(app)

# Configure CS50 Library to use SQLite database
db = SQL("sqlite:///courseworx.db")

# Configure server responses


@app.after_request
def after_request(response):
    """Ensure responses aren't cached"""
    response.headers["Cache-Control"] = "no-cache, no-store, must-revalidate"
    response.headers["Expires"] = 0
    response.headers["Pragma"] = "no-cache"
    return response


@app.route("/")
@login_required
def index():
    """Show portfolio of user assignments"""

    # Variable for time referencing
    current_datetime = datetime.now()

    # If student logged in
    if "student_id" in session:
        student_id = session["student_id"]

        # Get this student submissions and pending due their deadlines
        # Get all submissions  by this student due their deadlines
        submissions = db.execute("SELECT courses.course_code, courses.course_name, submissions.assignment_number, assignments.deadline FROM submissions JOIN assignments ON submissions.course_code = assignments.course_code JOIN courses ON assignments.course_code = courses.course_code WHERE assignments.deadline >= ? AND student_id = ? ORDER BY assignments.deadline ASC", current_datetime, student_id,)

        # Get all pending assignments for this student
        pendings = db.execute("SELECT * FROM assignments JOIN courses ON assignments.course_code = courses.course_code WHERE assignments.deadline >= ? AND (assignments.course_code, assignments.assignment_number) NOT IN (SELECT submissions.course_code, submissions.assignment_number FROM submissions WHERE student_id = ?) ORDER BY assignments.deadline ASC", current_datetime, student_id)

        # Render index template with variables submission and pending
        return render_template("index.html", pendings=pendings, submissions=submissions)

    # If Lecturer logged in
    if "lecturer_id" in session:
        lecturer_id = session["lecturer_id"]

        # Get all assignments issued by this lecturer that are due their deadlines
        assignments = db.execute(
            "SELECT * FROM assignments JOIN courses ON assignments.course_code = courses.course_code WHERE assignments.deadline >= ? AND lecturer_id = ? ORDER BY assignments.deadline ASC", current_datetime, lecturer_id)

        # Get status of submissions i.e submitted/total students
        total = db.execute("SELECT COUNT(*) FROM students")

        # Append the status of submissions on every assignment
        for assignment in assignments:
            course_code = assignment["course_code"]
            assignment_number = assignment["assignment_number"]
            submitted = db.execute("SELECT COUNT(*) FROM submissions JOIN assignments ON submissions.course_code = assignments.course_code WHERE submissions.course_code = ? AND submissions.assignment_number = ? AND assignments.deadline >= ? AND lecturer_id = ?",
                                   course_code, assignment_number, current_datetime, lecturer_id)
            assignment["submitted"] = submitted[0]["COUNT(*)"]
            assignment["total"] = total[0]["COUNT(*)"]

        # Render index template with variable assignments
        return render_template("index.html", assignments=assignments)


@app.route("/register", methods=["GET", "POST"])
def register():
    """Register Students and Lecturers"""

    # Render register template if method is GET
    if request.method == "GET":
        return render_template("register.html")

    # Else register user if method is POST
    # Store user input in variables
    name = (request.form.get("name")).strip()
    email = (request.form.get("email")).strip()
    password = request.form.get("password")
    confirmation = request.form.get("confirmation")
    name = request.form.get("confirmation")

    # Validate user input
    if not name or not email or not password or not confirmation:
        flash("Missing user details!", "danger")
        return redirect("/register")

    # Check if password and confirmation match
    if password != confirmation:
        flash("Sorry, Passwords do not match!", "danger")
        return redirect("/register")

    # Registration for Student
    if request.form["action"] == "register-student":

        # Try inserting student into students database
        try:
            db.execute("INSERT INTO students (student_name, student_email, hash) VALUES(?, ?, ?)",
                       name, email, generate_password_hash(password))
        except ValueError:
            flash("Student already exists!", "danger")
            return redirect("/register")

        # Remember student
        student = db.execute("SELECT * FROM students WHERE student_email = ?", email)
        session["student_id"] = student[0]["student_id"]
        flash("Student Registration Successful", "success")
        return redirect("/")

    # Registration for Lecturer
    if request.form["action"] == "register-lecturer":

        # Try inserting lecturer into lecturers database
        try:
            db.execute("INSERT INTO lecturers (lecturer_name, lecturer_email, hash) VALUES(?, ?, ?)",
                       name, email, generate_password_hash(password))
        except ValueError:
            flash("Lecturer already exists!", "danger")
            return redirect("/register")

        # Remember Lecturer
        lecturer = db.execute("SELECT * FROM lecturers WHERE lecturer_email = ?", email)
        session["lecturer_id"] = lecturer[0]["lecturer_id"]
        flash("Lecturer Registration Successful", "success")
        return redirect("/")


@app.route("/login", methods=["GET", "POST"])
def login():
    """Log user in"""

    # Forget any student_id or lecturer_id
    session.clear()

    # Render login template if method is GET
    if request.method == "GET":
        return render_template("login.html")

    # Else user reached route via POST (as by submitting a form via POST)
    # Validate user input
    email = (request.form.get("email")).strip()
    if not email:
        flash("Missing email!", "danger")
        return render_template("login.html")
    password = request.form.get("password")
    if not password:
        flash("Missing password!", "danger")
        return render_template("login.html")

    # Log in for Student
    if request.form["action"] == "login-student":

        # Query database for student
        student = db.execute("SELECT * FROM students WHERE student_email = ?", email)

        # Ensure student exists and password is correct
        if len(student) != 1 or not check_password_hash(student[0]["hash"], password):
            flash("Invalid Student email and/or password!", "danger")
            return render_template("login.html")

        # Remember which student has logged in
        session["student_id"] = student[0]["student_id"]

        # Redirect student to home page
        flash("Student Log in Successful", "success")
        return redirect("/")

    # Log in for Lecturer
    if request.form["action"] == "login-lecturer":

        # Query database for lecturer
        lecturer = db.execute("SELECT * FROM lecturers WHERE lecturer_email = ?", email)

        # Ensure lecturer exists and password is correct
        if len(lecturer) != 1 or not check_password_hash(lecturer[0]["hash"], password):
            flash("Invalid Lecturer email and/or password!", "danger")
            return render_template("login.html")

        # Remember which lecturer has logged in
        session["lecturer_id"] = lecturer[0]["lecturer_id"]

        # Redirect lecturer to home page
        flash("Lecturer Log in Successful", "success")
        return redirect("/")


@app.route("/logout")
def logout():
    """Log user out"""

    # Forget any user_id
    session.clear()

    # Redirect user to login form via index
    return redirect("/")


@app.route("/submit", methods=["GET", "POST"])
@login_required
def submit():
    """Submit assignment by Student"""

    # Variable for student_id reference
    student_id = session["student_id"]

    # Variable for time reference
    current_datetime = datetime.now()

    # Get all pending assignments for this student
    pendings = db.execute("SELECT * FROM assignments JOIN courses ON assignments.course_code = courses.course_code WHERE assignments.deadline >= ? AND (assignments.course_code, assignments.assignment_number) NOT IN (SELECT submissions.course_code, submissions.assignment_number FROM submissions WHERE student_id = ?) ORDER BY assignments.deadline ASC", current_datetime, student_id)

    # If student visits via POST method
    if request.method == "POST":

        # Validate student inputs
        course_code = request.form.get("course_code")
        if not course_code:
            flash("Missing Course Code!", "danger")
            return redirect(request.referrer)

        course_name = request.form.get("course_name")
        if not course_name:
            flash("Missing Course Name!", "danger")
            return redirect(request.referrer)

        assignment_number = request.form.get("assignment_number")
        if not assignment_number:
            flash("Missing Assignment Number!", "danger")
            return redirect(request.referrer)

        try:
            assignment_number = int(assignment_number)
        except ValueError:
            flash("Invalid Assignment Number!", "danger")
            return redirect(request.referrer)

        # Check for form data passed from resubmit template and store in variables
        if "form_data" in session:
            form_data = session.get("form_data", {})
            form_course_code = form_data.get("course_code")
            form_course_name = form_data.get("course_name")
            form_assignment_number = int(form_data.get("assignment_number"))

            # Check if form data matches current inputs
            if course_code == form_course_code and course_name == form_course_name and assignment_number == form_assignment_number:

                # Re-assign user input to form variables
                course_code = form_course_code
                course_name = form_course_name
                assignment_number = form_assignment_number

        # Else validate user inputs
        elif ("form_data" in session and course_code != form_course_code and course_name != form_course_name and assignment_number != form_assignment_number) or ("form_data" not in session):
            for pending in pendings:
                if pending["course_code"] == course_code and pending["course_name"] == course_name and pending["assignment_number"] == assignment_number:
                    # Valid assignment
                    break
            else:
                # Invalid assignment
                flash("Invalid Assignment!", "danger")
                return redirect(request.referrer)

        if "pdf" not in request.files:
            flash("Missing PDF file!", "danger")
            return redirect(request.referrer)

        # Retrieve pdf file
        pdf_file = request.files["pdf"]

        # Check if the pdf was selected
        if pdf_file.filename == "":
            flash("No PDF File selected!", "danger")
            return redirect(request.referrer)

        # Check for existing submission
        existing_submission = db.execute(
            "SELECT pdf FROM submissions WHERE student_id = ? AND course_code = ? AND assignment_number = ?", student_id, course_code, assignment_number)
        if existing_submission:
            old_file_path = existing_submission[0]["pdf"]

            # Delete the old file
            if os.path.exists(old_file_path):
                os.remove(old_file_path)

        # Save the new file
        if pdf_file and pdf_file.filename.endswith(".pdf"):

            # Create the folder name with nested structure
            folder_name = f"uploads/{course_code}/{assignment_number}/{student_id}/"

            # Check if the folder already exists
            if not os.path.exists(folder_name):

                # Create the nested directories
                os.makedirs(folder_name)

            file_path = os.path.join(folder_name, pdf_file.filename)
            pdf_file.save(file_path)

            # Insert new submissions or update existing submission
            time = datetime.now()
            try:
                db.execute("INSERT INTO submissions (submission_type, student_id, course_code, assignment_number, time, pdf) VALUES(?, ?, ?, ?, ?, ?)",
                           "new", student_id, course_code, assignment_number, time, file_path)
            except ValueError:
                db.execute("UPDATE submissions SET submission_type = ?, time = ? pdf = ? WHERE student_id = ? AND course_code = ? AND assignment_number = ?",
                           "resubmission", time, file_path, student_id, course_code, assignment_number)

            # Submission success
            flash("Submission Successful", "success")
            return redirect("/")

        else:
            flash("Invalid file type!", "danger")
            return redirect(request.referrer)

    # Else student visits via GET render pendings template
    return render_template("submit.html", pendings=pendings)


@app.route("/index-submit", methods=["GET", "POST"])
@login_required
def index_submit():
    """Submit student assignment receieved from Index Page"""

    if request.method == "POST":
        # Store Form Data in session
        session["form_data"] = request.form

    # Retrieve data from session
    form_data = session.get("form_data", {})
    course_code = form_data.get("course_code")
    course_name = form_data.get("course_name")
    assignment_number = int(form_data.get("assignment_number"))

    return render_template("indexsubmit.html", course_code=course_code, course_name=course_name, assignment_number=assignment_number)


@app.route("/resubmit", methods=["GET", "POST"])
@login_required
def resubmit():
    """Resubmit student assignment"""

    if request.method == "POST":
        # Store Form Data in session
        session["form_data"] = request.form

    # Retrieve data from session
    form_data = session.get("form_data", {})
    course_code = form_data.get("course_code")
    course_name = form_data.get("course_name")
    assignment_number = int(form_data.get("assignment_number"))

    return render_template("resubmit.html", course_code=course_code, course_name=course_name, assignment_number=assignment_number)


@app.route("/review", methods=["POST"])
@login_required
def review():
    """Show Review of student submisson"""

    # Variable for student_id reference
    student_id = session["student_id"]

    # Validate Student file request
    course_code = request.form.get("course_code")
    assignment_number = request.form.get("assignment_number")
    if not course_code or not assignment_number:
        flash("Missing Course Details!", "danger")
        if "history" in request.referrer:
            return redirect("/history")
        else:
            return redirect("/")
    try:
        assignment_number = int(assignment_number)
    except ValueError:
        flash("Invalid Assignment Number!", "danger")
        if "history" in request.referrer:
            return redirect("/history")
        else:
            return redirect("/")

    # Get file path
    file_path = db.execute("SELECT pdf FROM submissions WHERE student_id = ? AND course_code = ? AND assignment_number = ?",
                           student_id, course_code, assignment_number)

    if file_path and file_path[0]["pdf"]:
        return send_file(file_path[0]["pdf"], as_attachment=True)
    flash("File Not Found!", "danger")
    if "history" in request.referrer:
        return redirect("/history")
    else:
        return redirect("/")


@app.route("/add", methods=["GET", "POST"])
@login_required
def add():
    """Add assignment by Lecturer"""

    # Variable for lecturer_id reference
    lecturer_id = session["lecturer_id"]

    # Variable for time reference
    current_datetime = datetime.now()

    # All possible assignments should be valid courses
    assignments = db.execute(
        "SELECT courses.course_code, courses.course_name, MAX(assignments.assignment_number) AS assignment_number FROM courses LEFT JOIN assignments ON courses.course_code = assignments.course_code GROUP BY courses.course_code")

    # Get the assignment numbers for each course
    for assignment in assignments:

        # Update assignment numbers for existing and new assignments
        if assignment["assignment_number"] is None:
            assignment["assignment_number"] = 1
        else:
            assignment["assignment_number"] += 1

    # if user visits via GET route
    if request.method == "GET":
        return render_template("add.html", assignments=assignments)

    # Else user visits via POST method

    # Validate lecturer inputs
    course_code = request.form.get("course_code")
    if not course_code:
        flash("Missing Course Code!", "danger")
        return redirect(request.referrer)

    course_name = request.form.get("course_name")
    if not course_name:
        flash("Missing Course Name!", "danger")
        return redirect(request.referrer)

    assignment_number = request.form.get("assignment_number")
    if not assignment_number:
        flash("Missing Assignment Number!", "danger")
        return redirect(request.referrer)
    try:
        assignment_number = int(assignment_number)
    except ValueError:
        flash("Invalid Assignment Number!", "danger")
        return redirect(request.referrer)

    # Check for form data passed from adjust template and store in variables
    if "form_data" in session:
        form_data = session.get("form_data", {})
        form_course_code = form_data.get("course_code")
        form_course_name = form_data.get("course_name")
        form_assignment_number = int(form_data.get("assignment_number"))


        # Check if form data matches current inputs
        if course_code == form_course_code and course_name == form_course_name and assignment_number == form_assignment_number:
            # Re-assign user input to form variables
            course_code = form_course_code
            course_name = form_course_name
            assignment_number = form_assignment_number

    # Else validate user inputs
    elif ("form_data" in session and course_code != form_course_code and course_name != form_course_name and assignment_number != form_assignment_number) or ("form_data" not in session):
        for assignment in assignments:
            if assignment["course_code"] == course_code and assignment["course_name"] == course_name and assignment["assignment_number"] == assignment_number:
                # Valid assignment
                break
        else:
            # Invalid assignment
            flash("Invalid Assignment!", "danger")
            return redirect(request.referrer)

    # Validate deadline
    deadline = request.form.get("deadline")
    if not deadline:
        flash("Missing Assignment Deadline!", "danger")
        return redirect(request.referrer)
    try:
        deadline = datetime.fromisoformat(deadline)
    except ValueError:
        flash("Invalid datetime format!", "danger")
        return redirect(request.referrer)
    if deadline < current_datetime:
        print(current_datetime)
        flash("Deadline cannot be in the past!", "danger")
        return redirect(request.referrer)

    # Insert new assignment or update existing assignment
    try:
        db.execute("INSERT INTO assignments (assignment_type, lecturer_id, course_code, assignment_number, deadline) VALUES(?, ?, ?, ?, ?)",
                   "new", lecturer_id, course_code, assignment_number, deadline)
    except ValueError:
        db.execute("UPDATE assignments SET assignment_type = ?, deadline = ? WHERE lecturer_id = ? AND course_code = ? AND assignment_number = ?",
                   "extension", deadline, lecturer_id, course_code, assignment_number)

    # Submission success
    flash("Assignment Successful", "success")
    return redirect("/")


@app.route("/adjust", methods=["GET", "POST"])
@login_required
def adjust():
    """Adjust assignment deadline"""

    if request.method == "POST":
        # Store Form Data in session
        session["form_data"] = request.form

    # Retrieve data from session
    form_data = session.get("form_data", {})
    course_code = form_data.get("course_code")
    course_name = form_data.get("course_name")
    assignment_number = int(form_data.get("assignment_number"))
    deadline = form_data.get("deadline")

    return render_template("adjust.html", course_code=course_code, course_name=course_name, assignment_number=assignment_number, deadline=deadline)


@app.route("/history")
@login_required
def history():
    """Show history of assignments"""

    # Variable for time referencing
    current_datetime = datetime.now()

    # .strftime("%Y-%m-%d %H:%M:%S")

    # If student logged in
    if "student_id" in session:
        student_id = session["student_id"]

        past_assignments = db.execute("SELECT a.course_code, a.assignment_number, a.deadline, c.course_name, s.time AS time FROM assignments AS a JOIN courses AS c ON a.course_code = c.course_code LEFT JOIN     submissions AS s ON a.course_code = s.course_code AND a.assignment_number = s.assignment_number AND s.student_id = ? WHERE (s.time <= ? OR a.deadline <= ?) ORDER BY COALESCE(s.time, ?) DESC, a.deadline DESC", student_id, current_datetime, current_datetime, '9999-12-31')

        # Update submitted and missed assignments
        for assignment in past_assignments:
            if assignment["time"] is None:
                assignment["status"] = "Missed"
            else:
                assignment["status"] = "Submitted"

    # If Lecturer logged in
    if "lecturer_id" in session:
        lecturer_id = session["lecturer_id"]

        # Get all past assignments issued by this lecturer that are past their deadlines
        past_assignments = db.execute(
            "SELECT * FROM assignments JOIN courses ON assignments.course_code = courses.course_code WHERE assignments.deadline <= ? AND lecturer_id = ? ORDER BY assignments.deadline DESC", current_datetime, lecturer_id)

        # Get status of submissions i.e submitted/total students
        total = db.execute("SELECT COUNT(*) FROM students")

        print("AFTER TOTAL COUNT")

        # Append the status of submissions on every past assignment
        for assignment in past_assignments:
            course_code = assignment["course_code"]
            assignment_number = assignment["assignment_number"]

            submitted = db.execute("SELECT COUNT(*) FROM students JOIN submissions ON students.student_id = submissions.student_id WHERE students.student_id IN (SELECT student_id FROM submissions JOIN assignments ON submissions.course_code = assignments.course_code WHERE submissions.course_code = ? AND submissions.assignment_number = ? AND assignments.deadline <= ?)", course_code, assignment_number, current_datetime)

            assignment["submitted"] = submitted[0]["COUNT(*)"]
            assignment["total"] = total[0]["COUNT(*)"]

    print(past_assignments)

    # Render index template with variable assignments
    return render_template("history.html", past_assignments=past_assignments)


@app.route("/missing", methods=["POST"])
@login_required
def missing():
    """Show Missing students in submission"""

    # Validate lecturer inputs
    course_code = request.form.get("course_code")
    if not course_code:
        flash("Missing Course Code!", "danger")
        return redirect(request.referrer)

    course_name = request.form.get("course_name")
    if not course_name:
        flash("Missing Course Name!", "danger")
        return redirect(request.referrer)

    assignment_number = request.form.get("assignment_number")
    if not assignment_number:
        flash("Missing Assignment Number!", "danger")
        return redirect(request.referrer)
    try:
        assignment_number = int(assignment_number)
    except ValueError:
        flash("Invalid Assignment Number!", "danger")
        return redirect(request.referrer)

    assignment_deadline = request.form.get("assignment_deadline")
    if not assignment_deadline:
        flash("Missing Assignment Deadline!", "danger")
        return redirect(request.referrer)

    # List for validating assignments
    valid_assignments = db.execute(
        "SELECT * FROM courses JOIN assignments ON courses.course_code = assignments.course_code")

    # Validate if lecturer inputs are valid course assignments
    for assignment in valid_assignments:
        if assignment["course_code"] == course_code and assignment["course_name"] == course_name and assignment["assignment_number"] == assignment_number:
            # Valid assignment
            break
    else:
        # Invalid assignment
        flash("Invalid Assignment!", "danger")
        return redirect(request.referrer)

    # Get all missing students for this assignment by this lecturer
    missing = db.execute("SELECT students.student_id, student_name, student_email FROM students LEFT JOIN submissions ON students.student_id = submissions.student_id WHERE students.student_id NOT IN (SELECT student_id FROM submissions WHERE submissions.course_code = ? AND submissions.assignment_number = ?) ORDER BY students.student_id ASC", course_code, assignment_number)

    # Render missing template
    return render_template("missing.html", course_code=course_code, course_name=course_name, assignment_number=assignment_number, assignment_deadline=assignment_deadline, missing=missing)


@app.route("/download-all", methods=["POST"])
@login_required
def download_all():
    """Lecturer download all assignments"""

    # Validate lecturer file request
    course_code = request.form.get("course_code")
    assignment_number = request.form.get("assignment_number")
    if not course_code or not assignment_number:
        flash("Missing Course Details!", "danger")
        return redirect("/history")
    try:
        assignment_number = int(assignment_number)
    except ValueError:
        flash("Invalid Assignment Number!", "danger")
        return redirect("/history")

    # Validate student submission
    submissions = db.execute(
        "SELECT pdf FROM submissions WHERE course_code = ? AND assignment_number = ?", course_code, assignment_number)

    if not submissions:
        flash("No Files!", "danger")
        return redirect("/history")

    # Validate file paths
    invalid_file_paths = 0
    valid_file_paths = []
    for file_path in submissions:
        if not file_path["pdf"]:
            # Invalid file path
            invalid_file_paths += 1
        valid_file_paths.append(file_path["pdf"])

    # Create a BytesIO object to hold the zip file in memory
    zip_io = io.BytesIO()

    with zipfile.ZipFile(zip_io, 'w') as zipf:
        for file in valid_file_paths:
            zipf.write(file, os.path.basename(file))


    zip_filename = f"{course_code}submissions{assignment_number}.zip"

    # Seek to the beginning of the BytesIO object before sending
    zip_io.seek(0)
    return send_file(zip_io, download_name=zip_filename, as_attachment=True)
