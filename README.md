# About
A group scheduling application that takes inspiration from when2meet.com.

Add/edit schedules individually, then view common free times on the main screen. Save subsets of people as groups. Also allows for saving of the current schedules and groupings to a file, to retrieve later.

Basically functions similarly to when2meet, but allows for selecting only certain people so that you can schedule for different subgroups within the main group.

Runs on Python 3.

# How to Use
## Running the Application
Open the application by running 'python scheduler.py' from the command line. (note: ensure you are using python 3)

## Adding Schedules
To add/edit someone's schedule manually, type their name into the text input near the bottom, and press enter (or click the new/edit button).

  * A window will pop up where you can select the times they are free

To add schedules from .ics files, click "batch .ics add" and select the desired .ics files.

  * NOTE: files should be named for the person, e.g. "john doe.ics"

## Groups
Select the names you wish to group together from the list on the right, and click the "group" button. Name your group in the pop-up that appears. 

The "Groups" menu in the menubar gives you access to your saved groups.
To edit a group, edit your selection and save it under the same name.

## Saving/Loading
Clicking the "save" button at the bottom left will allow you to save your names and groups.

Clicking the "load" button at the bottom will allow you to load a previously saved file.

  * NOTE: loading will overwrite all existing schedules

## Viewing Availability
The numbers displayed on the calendar represent the number of people busy at that time.

To view the specific people available at some time slot, check "Availability" under the "View" menu, and hover over the calendar.

## Color Schemes
Select your desired color scheme under the "Theme" menu.

---

*Author: Arisha Kulshrestha  
Email: arishak@gmail.com*
