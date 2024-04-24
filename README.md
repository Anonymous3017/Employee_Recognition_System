# Installation

1. Clone the repository:
    ```
    git clone <repository_url>
    ```

2. Install dependencies:
    ```
    pip install -r requirements.txt
    ```

3. Configure AWS credentials in `~/.aws/credentials`.

4. Update the Flask app with your preferred routes and HTML templates.

# Usage

1. Run the Flask app:
    ```
    python app.py
    ```

2. Access the application via a web browser.

3. Upload images of employees or visitors.

4. View matched employee information and add new employees to the system.

# Endpoints

- `/`: Landing page
- `/addUser`: Add new user page
- `/upload`: Handle file upload and perform image matching
- `/add_employee`: Add a new employee to the system

# Dependencies

- Python 3.x
- Flask
- Boto3

# AWS Services Used

- Amazon Rekognition
- Amazon S3
- DynamoDB
