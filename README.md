# e-commerce
Ecommerce platform

# Django REST API

This repository contains a Django REST API with functionalities for uploading data, generating summary reports, and user authentication.

## Features

- **User Authentication**: Endpoints for user registration and login using JWT.
- **Upload Data**: Endpoint to upload CSV files containing product data.
- **Generate Summary Report**: Endpoint to generate and download a CSV summary report.


### Endpoints
1. SignUpView
POST /auth/signup

Create user.

    Request Body:
    json
    {
        "fullname": "Rajesh Kumar",
        "username": "test1",
        "password": "Test@12",
        "email": "test123@gmail.com"
    }
    Response:
        200 OK: Returns "User created successfully"
        400 Bad Request: If user creation fails

2. LoginView
POST /auth/login

Login user.

    Request Body:
    json
    {
        "username": "test1",
        "password": "Test@12"
    }
    Response:
        200 OK: Returns Access token and refresh token
        400 Bad Request: Failure

3. UploadData
POST /product/upload/data

Upload data to DB from csv file.

    Request Body:
    json
    {
        "csv_path":"SampleProductData.csv"
    }

    Response:
        200 OK: Returns "Data uploaded successfully"
        400 Bad Request: "Data upload failed"

4. SummaryReport
GET /get/summary/report

Get summary report.

    Response:
        200 OK: Returns Summary report in form of csv
        400 Bad Request: "Failed to create summary report"


## Setup
Prerequisites

    Python 3.x
    Django
    Django REST framework

Installation
    Clone the repository:
    sh

https://github.com/rajesh196rsh/e-commerce.git
cd e-commerce

### create virtual environemnt
virtualenv venv

### activate virtual environment
source venv/bin/activate

### Install the dependencies:
pip install -r requirements.txt

cd e_commerce_platform

### Apply the migrations:
python manage.py migrate

### Run the development server:
python manage.py runserver

Configuration

    Update the constants.py file with appropriate messages and settings.
    Ensure that your database settings in settings.py are configured correctly.

