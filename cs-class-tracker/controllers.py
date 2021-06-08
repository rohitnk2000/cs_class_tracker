"""
This file defines actions, i.e. functions the URLs are mapped into
The @action(path) decorator exposed the function at URL:

    http://127.0.0.1:8000/{app_name}/{path}

If app_name == '_default' then simply

    http://127.0.0.1:8000/{path}

If path == 'index' it can be omitted:

    http://127.0.0.1:8000/

The path follows the bottlepy syntax.

@action.uses('generic.html')  indicates that the action uses the generic.html template
@action.uses(session)         indicates that the action uses the session
@action.uses(db)              indicates that the action uses the db
@action.uses(T)               indicates that the action uses the i18n & pluralization
@action.uses(auth.user)       indicates that the action requires a logged in user
@action.uses(auth)            indicates that the action requires the auth object

session, db, T, auth, and tempates are examples of Fixtures.
Warning: Fixtures MUST be declared with @action.uses({fixtures}) else your app will result in undefined behavior
"""

from py4web import action, request, abort, redirect, URL
from yatl.helpers import A
from . common import db, session, T, cache, auth, logger, authenticated, unauthenticated, flash
from py4web.utils.url_signer import URLSigner
from . models import get_user_email
from py4web.utils.form import Form, FormStyleBulma

import uuid
import random

url_signer = URLSigner(session)


#########################
# Main Index Page
# -> displays all classes and allows students to sign up/remove
#########################
@action('index')
@action.uses(db, auth.user, 'index.html')
def index():
    
    rows = db(db.cs_class).select().as_list()
    for row in rows:
       
        studentList =  db(db.student.class_id == row['id']).select().as_list()
        s = ""
        for student in studentList:
            if student["student_name"]:
                s += student['student_name'] + " | "
       
        row["students"] = s

    classes = db(db.student.student_email == auth.current_user.get('email')).select().as_list()
    
    classesTaken = []
    for course in classes:
        className = db.cs_class[course["class_id"]]
        if className:
            classesTaken.append(className["className"])
  
    all_students = db(db.student).select().as_list()
    friends = db(db.friends_list).select().as_list()
    friend_classes = []
    for student in all_students:
        for friend in friends:
            if student["student_email"] == friend["friend_email"]:
                friend_classes.append(student["class_id"])

    student_record = db(db.student.student_email == auth.current_user.get("email")).select().as_list()
    student_info = []
    student_info.append(auth.current_user.get("first_name") + " " + auth.current_user.get("last_name"))
    student_info.append(auth.current_user.get("email"))  
    
    return dict(rows = rows, url_signer = url_signer, student_info = student_info, classesTaken = classesTaken, friend_classes = friend_classes)



#########################
# See Classmates
# -> shows full list of all students with emails
#########################
@action('see_classmates/<class_id:int>', method=["GET", "POST"])
@action.uses(db, session, auth.user, 'see_classmates.html')
def see_classmates(class_id = None):
    assert class_id is not None
    p = db.cs_class[class_id]
    if p is None:
        redirect(URL('index'))
    rows = db(db.student.class_id == class_id).select()
    return dict(rows=rows, className = p['className'])


#########################
# Add Student
# -> Adds a student to the student table under this specific class ID
#########################
@action('add_student/<class_id:int>', method=["GET", "POST"])
@action.uses(db, session, auth.user, 'add_student.html')
def add_student(class_id = None):
    assert class_id is not None
    p = db.cs_class[class_id]
    if p is None:
        redirect(URL('index'))
    student_record = db(db.student.student_email == auth.current_user.get("email")).select().as_list()
    
    db.student.insert(class_id = class_id, student_name = auth.current_user.get("first_name") + " " + auth.current_user.get("last_name"), 
                            student_email = auth.current_user.get("email"))
    redirect(URL('index'))


#########################
# Edit Friends
# -> Main friend page with search functionality and removing friends
#########################
@action('edit_friends', method=["GET", "POST"])
@action.uses(db, session, auth.user, 'edit_friends.html')
def edit_friends():
    rows = db(db.friends_list.user_email == auth.current_user.get("email")).select()

    return dict(rows=rows, search_url=URL('search', signer=url_signer))
    

#########################
# Search
# -> Uses Vue.js to instantly update search results on edit_friends page
#########################
@action('search')
@action.uses()
def search():
    q = request.params.get("q")
    students = db(db.student.student_email != auth.current_user.get("email")).select().as_list()
    searchList = []
    names = []
    for student in students:
        if student["student_name"] not in names:
            searchList.append(student)
            names.append(student["student_name"])
    
    results = []
    
    for item in searchList:
        if q.upper() in item["student_name"].upper():
            results.append(item)
    return dict(results=results)



#########################
# Remove Student 
# -> Removes a student from a class
#########################
@action('remove_student/<class_id:int>', method=["GET", "POST"])
@action.uses(db, session, auth.user)
def remove_student(class_id=None):
    assert class_id is not None
    db((db.student.student_email == auth.current_user.get("email")) & (db.student.class_id == class_id)).delete()
    redirect(URL('index'))



#########################
# Remove Friend 
# -> Removes friend from friends list
#########################
@action('remove_friend/<friend_id:int>', method=["GET", "POST"])
@action.uses(db, session, auth.user)
def remove_friend(friend_id=None):
    assert friend_id is not None
    db(db.friends_list.id == friend_id).delete()
    redirect(URL('edit_friends'))



#########################
# Add Friend 
# -> Adds friend from search list into class
#########################
@action('add_friend/<friend_id:int>', method=["GET", "POST"])
@action.uses(db, session, auth.user)
def add_friend(friend_id=None):
    assert friend_id is not None
    friend = db(db.student.id == friend_id).select().as_list()
    if len(friend) > 0:
        db.friends_list.update_or_insert(user_email = auth.current_user.get("email"), friend_name = friend[0]["student_name"],
                                    friend_email = friend[0]["student_email"] )
    
    redirect(URL('edit_friends'))





    