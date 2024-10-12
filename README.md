# COURSEWORX

#### Video Demo: [https://youtu.be/Xxrt9sAlRpA](https://youtu.be/Xxrt9sAlRpA)

#### Description:
This project is an extension of the ideas learned through CS50 and serves as a special dedication to the human force behind CS50. The project is a web application designed to facilitate student submissions of their assignments, generate a credible record of submissions, and allow lecturers to post assignments, providing a uniform and open platform for all these assignments.

### Introduction
The **COURSEWORX** application is developed to address the needs of both students and lecturers in the educational space. With the increasing shift towards online learning, there is a pressing need for a reliable and user-friendly platform that can facilitate the submission of assignments. This project serves as a tribute to the impactful teachings of CS50, encapsulating the essence of learning, collaboration, and accountability in education.

### Features
**For Lecturers:**
- **Assignment Management**: Lecturers can easily create, and update assignments, ensuring that the course material is always up to date.
- **Submission Monitoring**: They have access to real-time statistics showing submission rates, allowing them to identify students who may need additional support.
- **Flexible Deadlines**: Lecturers can modify deadlines as necessary, accommodating different learning paces and unexpected challenges.
- **Submission History**: They can view the history of submissions for their assignments, providing insight into student engagement and performance.
- **Download Functionality**: Lecturers can download all student submissions after the deadline, making it easier to review and assess assignments.

**For Students:**
- **Submission Tracking**: Students can view their submission status and deadlines, helping them stay organized and on top of their coursework.
- **Resubmission Capability**: If a student needs to make changes to their work, they can resubmit their assignments until the deadline, ensuring they have the opportunity to improve.
- **Historical Data Access**: The platform allows students to review their past submissions, providing insights into their progress and areas for improvement.
- **User-Friendly Interface**: The application is designed with an intuitive interface, making it easy for students to navigate and complete their tasks.

### Installation Instructions
To set up the COURSEWORX application on your local machine, follow these steps:
1. **Clone the Repository**: Use `git clone <repository-url>` to clone the project.
2. **Install Dependencies**: Navigate to the project directory and run `pip install -r requirements.txt` to install necessary packages.
3. **Set Up the Database**: Run the initialization script to create the required database tables.
4. **Start the Application**: Use `flask run` to start the web server.
5. **Access the Application**: Open a web browser and navigate to `http://127.0.0.1:5000` to access the platform.

### Usage Examples
- **Submitting Assignments**: Students can log in, navigate to their courses, and submit their assignments directly through the platform.
- **Viewing Submissions**: Lecturers can log in to view how many students have submitted their assignments and which students may need follow-up.
- **Adjusting Deadlines**: Lecturers can easily adjust the deadlines of assignments based on class needs.

### Future Improvements
- **Enhanced Notification System**: Implementing an email or SMS notification system to alert students about upcoming deadlines and submission statuses.
- **Integration with Learning Management Systems (LMS)**: Exploring the possibility of integrating with popular LMS platforms to streamline assignment management.
- **User Feedback Mechanism**: Adding a feedback feature for students to provide input on assignments and the platform itself.

### Contributing
Contributions to COURSEWORX are welcome! If you'd like to contribute, please follow these steps:
1. Fork the repository.
2. Create a new branch (`git checkout -b feature-branch`).
3. Make your changes and commit them (`git commit -m 'Add new feature'`).
4. Push to the branch (`git push origin feature-branch`).
5. Open a pull request.

### License
This project is licensed under the MIT License. See the LICENSE file for details.

### Contact Information
For support or inquiries, please reach out to:
- **Author**: Ronald Bagampange
- **Email**: [your-email@example.com]

#### FrontEnd:
* HTML
* CSS
* Javascript
* Bootstrap
* Jinja

#### BackEnd:
* Python
* Flask

#### Database:
* Sqlite3

#### Requirements:
* cs50
* Flask
* Flask-Session
* pytz
* requests

#### Files:
**Static**
CSS and Javascript.

**templates**
Layout template and all HTML templates for the project.

**Uploads**
Uploads of the students
* A little design implementation where every assignment gets a folder created in the corresponding course code folder.

**app.py**
A Flask web app that handles the backend of the application.

**helpers.py**
Contains the login required Python program.

**courseworx.db**
The database of the application includes tables for students, lecturers, courses, assignments, and submissions.

#### Acknowledgements:
* CS50
* design50
* Style50

#### Author:
Ronald Bagampange
