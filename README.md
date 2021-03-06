# Testing application - Task list

A Django web application to show relevant Django and Python skills, focusing on testing.

## Live Demo
Available at:
http://kask.io:1919/

There are 5 users created already. Passwords should have been sent to you.

Users: user0,user1,user2,user3,user4 

## Description
Following the assigment, a list of all tasks is presented. Each task may be marked as done by anyone. Delete and Edit options are available for a Tasks owner. An add button allows creating New tasks.


## Installation
(tested with Python 3.6.6)

```bash

pip install django==1.11

git clone https://github.com/jumarti/origin.git

cd origin/origin

# sync DB
python manage.py migrate

# Create 5 (or any number) users with a shared password
python create_users.py 5 <password>
#The user names are created as `user0`, `user1` ... `userN`

```

Run the webserver
```
python manage.py runserver
```

## Testing
Run the Django tests
```
python manage.py test
```


## A word on the design choice
This web application is a multi-page application. The reason for this as oppossed to a single page app is because the UX requirements are simple and it is clear from the assigment that focus should be on the Python-Django side of the development. 


## For managing users
Please use the Django admin at : `/admin`

