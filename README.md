# Web Application Exercise

A little exercise to build a web application following an agile development process. See the [instructions](instructions.md) for more detail.

## Product vision statement

As a student, I want to track my job applications so I can organize deadlines and follow up efficiently.

## User stories

### Authentication

- As a user, I want to stay logged in after closing the tab so that I don’t have to re-enter my credentials every time.
- As a user, I want to log out securely so that others cannot access my data on shared devices.
- As a user, I want to receive clear error messages if login or signup fails so that I know what went wrong (e.g., invalid password or existing email).
- As a user, I want to reset my password so that I can regain access if I forget it. (Tentative)

### Interface

- As a user, I want to see a confirmation message when I add, edit, or delete a job so that I know the action was successful.
- As a user, I want to sort my applications by deadline, company, or status so that I can prioritize easily.
- As a user, I want to view color-coded statuses (e.g., green for offers, red for rejections) so that I can recognize progress at a glance.
- As a user, I want to view an application's details in a clean, mobile-friendly layout so that I can quickly read and update information on my phone.
- As a user, I want clear validation and success/error messages when updating my profile so I know what happened.

### Analytics

- As a user, I want to see a chart showing my applications over time so that I can track how actively I’m applying.
- As a user, I want to see a breakdown of applications by company or location so that I can identify patterns in my search.
- As a user, I want to see success rates per stage (e.g., OA → Interview → Offer) so that I can reflect on where to improve.

### Data

1. As a user, I want to attach notes to each application so that I can record interview details and follow-up thoughts.
2. As a user, I want to mark an application as ‘Archived’ so that I can keep my dashboard focused only on active ones.
3. As a user, I want my data to be timestamped (created / updated) so that I can see how recent each entry is.
4. As a user, I want my input forms to validate required fields (title, company, deadline) so that incomplete entries don’t break the dashboard.
5. As a user, I want automatic sorting of applications by deadline so that the most urgent ones appear first.
6. As a user, I want the system to prevent duplicate entries for the same role and company so that my data stays clean.
7. As a user, I want to view my profile (name, pronouns, graduation term, year) so I can confirm what the app has on file.
8. As a user, I want to edit and save my profile so my information stays current.

## Steps necessary to run the software

1. Clone the repository

Use the command below to download the project to your computer:

`git clone https://github.com/swe-students-fall2025/2-web-app-salamander.git`

2. Install the dependencies

Run the following command to install the necessary dependencies:

`pip install -r requirements.txt`

3. Create your own .env file

Copy the example env file to your own by running the following command:

`cp env.example .env`

4. Run the Flask App

``` bash
flask --app app run --debug
```

### Directory Layout


``` bash
app/
  __init__.py            # create_app()
  db.py                  # DB connection 
  models/
    __init__.py
    user.py              # User model logic
    application.py       # Job application model
  auth/                  # handles login/signup/logout
    __init__.py
    routes.py
    templates/
      login.html
      signup.html
  dashboard/             # main CRUD + search
    __init__.py
    routes.py
    templates/
      dashboard.html
      new.html
      edit.html
  static/                # styling
    css/
      styles.css
    js/
      dashboard.js

```

## Task boards

https://github.com/users/axie22/projects/2/views/1
