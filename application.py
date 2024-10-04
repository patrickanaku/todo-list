import os
import json
from flask import Flask, request, render_template
from datetime import date
from filelock import FileLock, Timeout

# Defining Flask App
application = Flask(__name__)

# Saving Date today in a readable format
datetoday2 = date.today().strftime("%d-%B-%Y")

# If this file doesn't exist, create it
if not os.path.exists('tasks.json'):
    with open('tasks.json', 'w') as f:
        json.dump([], f)  # Initialize with an empty list


# Helper function to handle file access with locking for concurrency using filelock
def GetTaskList():
    try:
        lock = FileLock("tasks.json.lock", timeout=10)
        with lock:
            with open('tasks.json', 'r') as f:
                tasklist = json.load(f)
        return tasklist
    except Timeout:
        print("Could not acquire the lock.")
        return []  # Return empty list if unable to lock file
    except (IOError, json.JSONDecodeError):
        print("Error reading tasks.json.")
        return []  # Return empty list if file reading fails


def UpdateTaskList(tasklist):
    try:
        lock = FileLock("tasks.json.lock", timeout=10)
        with lock:
            with open('tasks.json', 'w') as f:
                json.dump(tasklist, f)
    except Timeout:
        print("Could not acquire the lock to write.")
    except IOError:
        print("Error writing to tasks.json.")


# -------------------- ROUTING FUNCTIONS --------------------

# Our main page
@application.route('/')
def home():
    return render_template('home.html', datetoday2=datetoday2, tasklist=GetTaskList(), l=len(GetTaskList()), mess='')


# Function to clear the to-do list
@application.route('/clear')
def clear_list():
    UpdateTaskList([])  # Clear the task list
    return render_template('home.html', datetoday2=datetoday2, tasklist=[], l=0, mess='Task list cleared!')


# Function to add a task to the to-do list
@application.route('/addtask', methods=['POST'])
def add_task():
    task = request.form.get('newtask')

    if task and task.strip():  # Check if the task is not empty
        tasklist = GetTaskList()
        task = task.strip()  # Clean up extra spaces

        if task in tasklist:  # Check for duplicate tasks
            message = 'Task already exists!'
        else:
            tasklist.append(task)  # Add new task
            UpdateTaskList(tasklist)
            message = 'Task added successfully!'
    else:
        message = 'Please enter a valid task.'

    return render_template('home.html', datetoday2=datetoday2, tasklist=GetTaskList(), l=len(GetTaskList()),
                           mess=message)


# Function to remove a task from the to-do list
@application.route('/deltask', methods=['GET'])
def remove_task():
    try:
        task_index = int(request.args.get('deltaskid'))
        tasklist = GetTaskList()

        if 0 <= task_index < len(tasklist):  # Ensure valid index
            removed_task = tasklist.pop(task_index)
            UpdateTaskList(tasklist)
            message = f'Task "{removed_task}" removed successfully!'
        else:
            message = 'Invalid task index.'

    except (ValueError, TypeError):
        message = 'Invalid input for task index.'

    return render_template('home.html', datetoday2=datetoday2, tasklist=tasklist, l=len(tasklist), mess=message)


# main function which runs the Flask App
if __name__ == '__main__':
    application.run(host='0.0.0.0')
