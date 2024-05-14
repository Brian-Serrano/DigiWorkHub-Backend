# DigiWork Hub
Task Management Android Application for Department of Information and Communications Technology workers. I cannot guarantee that I can provide the best documentation for my application. I am only a programmer.

## Features
1. Task:
   1. Assignees = The users that will complete task the creator create. Assignees should only have up to 5 users. Only the creator of task can change the assignees.
   2. Type = The possible type of tasks are TASK and MILESTONE. Only the creator of the task can edit.
   3. Priority = The possible priority of tasks are LOW, NORMAL, HIGH and URGENT. Only the creator of the task can edit.
   4. Status = The possible status of tasks are OPEN, IN PROGRESS, ON HOLD and COMPLETE. Only the assignees of the task can edit.
   5. Due date = The date when the task should be done. Due date should not be less than the date the task created. If the current date is greater than the due date, means the due date has been reached and the box color of due date will change from color green to color red. But the task status can still be edited by assignee. Even the task reached the due date the assignees can still be able to complete it and the task will still be seen in the dashboard or about task menu. Only the creator of task can edit.
   6. Title = The name/title of the task. Title should be 15-100 characters. Only the creator of task can edit.
   7. Description = The description of the task. Description should be 50-1000 characters. Only the creator of task can edit.
   8. Sent date = When the task created. This is automatically generated upon creation of task and this cannot be edited by any user.
   9. Creator = The creator of task.
   10. Comments:
       1. Description = The text what the user wants to comment. Should be 10-500 characters. The creator and assignees of task can send comments.
       2. Like = The creator and assignees of task can like comments. They can also unlike the comment anytime.
       3. Mentions = The user that will send the comment can mention other assignees or the creator of task.
       4. Reply = The user can reply to a comment of another user.
       5. Sent date = The date the comment sent.
       6. Comments can be deleted and this can only done by the user that send the comment.
   11. Checklist:
       1. Description = The information about the checklist. Should be 50-1000 characters. The creator and assignees of task can add checklists.
       2. Assignees = The users that will complete the checklist. Assignees should be up to 5 users and task assignees and creator can only added as checklist assignee. The assignees only can check/uncheck the checklist.
       3. Sent date = The date the checklist created.
       4. Checklists can be deleted and this can only done by the user that create the checklist.
   12. Subtask:
       1. Description = The information about the subtask. Should be 50-1000 characters. The creator and assignees of task can add subtasks. Only the creator of subtask can edit description.
       2. Status = The possible status of subtasks are OPEN, IN PROGRESS, ON HOLD and COMPLETE. Only the assignees of subtask can edit status.
       3. Priority = The possible priority of subtasks are LOW, NORMAL, HIGH and URGENT. Only the creator of the subtask can edit.
       4. Type = The possible type of subtasks are TASK and MILESTONE. Only the creator of the subtask can edit.
       5. Due date = The date when the subtask should be done. Due date should not be less than the date the subtask created. If the current date is greater than the due date, means the due date has been reached. But the subtask status can still be edited by assignee. Even the subtask reached the due date the assignees can still be able to complete it and the subtask will still be seen in the about task menu. Only the creator of subtask can edit.
       6. Assignees = The users that will complete subtask. Assignees should be up to 5 users and task assignees and creator can only added as subtask assignee. Only the creator of subtask can change the assignees.
       7. Sent date = The date the subtask created.
       8. Subtasks can be deleted and this can only done by the user that create the subtask.
   13. Attachment = A file that a creator or assignee of the task can send. The maximum file size is 50 mb. The allowed file extensions are: `{"7z", "aac", "accdb", "accft", "adx", "ai", "aiff", "aifc", "amr", "amv", "avi", "avif", "bmp", "blend", "cdf", "cdr", "cgm", "csv", "doc", "docx", "docm", "dot", "dotx", "dpx", "drc", "dtd", "dwf", "dwg", "dxf", "email", "emf", "eml", "emz", "eot", "esd", "exp", "f4v", "fbx", "flac", "flv", "fni", "fnx", "fodg", "fodp", "fods", "fodt", "gif", "gz", "hdi", "icl", "ico", "img", "info", "iso", "j2c", "jp2", "jpe", "jpeg", "jpg", "json", "jxl", "ldb", "lz", "m3u", "m3u8", "m4a", "m4p", "m4r", "m4v", "md", "mdf", "mdi", "mov", "mp2", "mp3", "mp4", "mpa", "mpc", "mpeg", "mpg", "mso", "mxf", "odb", "odf", "odg", "odp", "ods", "odt", "oga", "ogg", "ogv", "ogx", "ost", "otf", "otg", "otp", "ots", "ott", "pdf", "pgn", "png", "pptx", "ppsx", "ppt", "psd", "psdc", "pub", "rar", "rtf", "svg", "swf", "stc", "std", "sti", "stw", "sxc", "sxd", "sxg", "sxi", "sxm", "sxw", "tak", "tar", "taz", "tb2", "tbz", "tbz2", "tif", tiff", "torrent", "ttc", "ttf", "url", "uxf", "wav", "webm", "wma", "wmdb", "wmf", "wmv", "wtx", "xls", "xlsb", "xlsm", "xlsx", "xmf", "xml", "xps", "zip"}`. The file can be downloaded to users device. The attachment can be deleted by the user who send it.
   14. Tasks can be deleted by the user creates it.
2. Messaging:
   1. Title = The subject of the message. Should be 15-100 characters.
   2. Description = The information of message. Should be 50-3000 characters.
   3. Attachment = The user can also send up to 5 attachments to the recipient with the message.
   4. Sent date = The date the message was sent.
   5. Reply = The sender or receiver of the message can send reply to the message. The reply should be 10-500 characters. The reply can also have up to 5 attachments on it. The reply has sent date. The reply can be deleted by the user send it.
   6. The message can be deleted by the user who send it and both sender and receiver can not see it anymore. The message can also be deleted only from the sender. The receiver can still see the message but not the sender. If the receiver send reply to the message, the sender that deleted it can see the message again. The message can also be deleted only from the receiver. The sender can still see the message but not the receiver. If the sender send reply to the message, the receiver that deleted it can see the message again.
3. User:
   1. Username = Should only have alphanumeric, underscore and space characters. Username can be change in profile and settings.
   2. Email Address = Any domain can be accepted but it should exist, this can be used if you forgot password. Email address cannot be changed.
   3. Password = Should have at least one letter and number, and 8-20 characters. Password can be edited in settings but need to enter the previous password and confirm the password to change it. Password can also be change in login (where the user is unauthorized) by the forgot password. This do not require the previous password but you need additional steps to change it. Make sure the email text field have your valid email address and you can click the forgot password. The application will send the mail to you with the code and you must enter that code in the application and can change the password.
   4. Role = Should be 5-50 characters. The default value is NA. You can edit role in profile and settings.
   5. Image = You can upload any valid image and the application will automatically scale/crop it to 200x200 pixel size. The image can be change in profile and settings. A default image is auto generated after signing up with random background color and a letter with the first letter of username in uppercase.
   6. A user can delete his/her account.
4. Signing Up and Logging in = The signup and login have validation checks on every letter you enter in fields. It has also validation on the backend-side.
5. Organize tasks = In the task menu, you can group the tasks by its status, priority, type, due date and creator. And the grouped tasks can each be collapse/un-collapse. You can also filter the tasks with the value in status, priority, type, due date and creator and show only what is the value only matched/unmatched in the tasks. You can also sort the tasks by the name, assignee size, due date, priority, type and status lexicographically and ascending order.
6. Task views = List View, Grid View, Calendar View.
7. Data (Tasks/Messages) Caching = This application requires internet connection. Using network data everytime you navigate to different pages will consume more of your data. The application implements caching by using the Room library to save the data got from the server locally and use it instead if you navigate to the same page. And no need network data open once the data has got on that page. And you kill the application and launch again will still show the same data of page. But editing/adding/deleting task or sending messages require network data to work. The user can retrieve the latest data (tasks/messages) (if there are any cached to that page) by swiping down to refresh the page.
8. Users can directly edit tasks in dashboard and about task menu.
9. When image of users are created in the server, their names are the date when they created. The server will not use the name of the image where the image come from. This make sure that name of images are unique and avoid wrong image shown. When an attachment uploaded the date when the attachment uploaded is the name followed by `_idx_<idx>` where <idx> is a number when the request have multiple attachments (used in message and reply message). The original name of attachments where it come from will be save in database and it will be used and shown in the user interface (about task page) as the file name. The name of the attachments in the server (unique) will be used to determine which files to download. When the file will be stored in users device shared storage the name is the original name of the attachment and date when the attachment stored in the device appended. This make sure that nothing attachment download bug occurred. I use media store to store the attachments. If you can find out why it bugs when I do not add date to the last of the file name and know how to fix it. Then you can fix it and you can remove the date associated.

## Frontend Frameworks/Libraries
1. Jetpack Compose = Android’s modern toolkit for building native UI. Simplifies and accelerates UI development on Android with less code, powerful tools, and intuitive Kotlin APIs.
2. Dagger Hilt = A dependency injection library for Android that reduces the boilerplate of doing manual dependency injection in project. Doing manual dependency injection requires to construct every class and its dependencies by hand, and to use containers to reuse and manage dependencies.
3. Firebase Cloud Messaging = Firebase Cloud Messaging (FCM) is a cross-platform messaging solution that lets you reliably send messages at no cost. Using FCM, you can notify a client app that new email or other data is available to sync. You can send notification messages to drive user re-engagement and retention. For use cases such as instant messaging, a message can transfer a payload of up to 4096 bytes to a client app. The application uses FCM for push notifications.
4. DataStore = A data storage solution that allows you to store typed objects. DataStore uses Kotlin coroutines and Flow to store data asynchronously, consistently, and transactional. The application uses DataStore for saving the user data (images, tokens, etc.) in internal storage.
5. Retrofit = A type-safe HTTP client for Android. The application uses Retrofit for doing HTTP request to the application backend.
6. Gson = A Java library that can be used to convert Java Objects into their JSON representation. Retrofit/Application uses gson to map requests from Kotlin objects to JSON and map responses from JSON to Kotlin objects.
7. Okhttp = HTTP Client used by the application for logging (for easy debugging), and interceptor (authorization interceptor for backend routes that require authorization).
8. Java JWT = Used by the application to check validity and expiration json web tokens of users.
9. Material Icons Extended = Contains the full set of Material icons. Used by the application for the icons that do not exist in the default Material Icons.
10. Swipe Refresh = Used for refreshing data (request backend data) in the page by swiping vertically.
11. Room = Used for saving the tasks/messages from backend locally to be able to browse them even the user is offline.

## Backend Frameworks/Libraries
1. Flask = Lightweight WSGI web application framework. It is designed to make getting started quick and easy, with the ability to scale up to complex applications. It began as a simple wrapper around Werkzeug and Jinja, and has become one of the most popular Python web application frameworks.
2. Bcrypt = Password Hashing Library for Python.
3. Firebase Admin = The Admin SDK is a set of server libraries that lets you interact with Firebase from privileged environments to perform actions.
4. Pillow = Built on top of PIL. Python Imaging Library (PIL) adds image processing capabilities to Python interpreter.
5. PyJWT = A Python library which allows you to encode and decode JSON Web Tokens (JWT). JWT is an open, industry-standard for representing claims securely between two parties.
6. SQLAlchemy = Python SQL toolkit and Object Relational Mapper that gives application developers the full power and flexibility of SQL.

## Environment Variables (make your own)
1. DIGIWORKHUB_DB_URI = path to database file
2. EMAIL_REGEX = pattern for matching email address
3. NAME_REGEX = pattern for matching username
4. PASSWORD = google password for sending mails to users
5. PASSWORD_REGEX = pattern for matching password
6. SALT = bcrypt password hashing salt
7. SECRET_KEY = jwt decode/encode secret key

## Three types of objects
1. Data Transfer Objects = These objects are used by the HTTP Client in requesting server as request objects or response objects.
2. State Objects = These objects are used by the user interface.
3. Entity Objects = These objects are used by the room database.

## More Information
1. Frontend Programming Language = Kotlin
2. Frontend IDE = Android Studio
3. Run Frontend Application = If you have not the application/code in your device you can clone it in github and use Android Studio to run it. You might also need to edit some configurations.
4. Backend Programming Language = Python
5. Backend IDE = Pycharm
6. Run Backend Application = If you have not the application/code in your device you can clone it in github and use Pycharm to run it or you can use others like VS Code. You need to create `python -m venv .venv` and activate `.venv\Scripts\activate` virtual environment and install requirements.txt `pip install -r requirements.txt` before running it.
7. Deployment = This application in my Github Repository is deployed in render.com. But it has some limitations and not good for production applications that are using by all branches of DICT. Deploying it on that platform with limitations is only for testing purposes. You can deploy it to other platform. I will push this code to other Github Repository and not connected in render.com anymore. If you test this application with localhost or other hosting platform, make sure to replace the base url in api module.
8. Firebase Cloud Messaging Files = Create your own google-services.json file in frontend and service_account_key.json in backend to be able to use FCM for push notifications. I have created my own but this is private and should not be shared to other users and not pushed as I added it to .gitignore. Make sure to sign in in firebase and create your own project.

## Frontend Architecture
![Frontend](README%20images/Frontend-Architecture.png)

## Backend Architecture
![Backend](README%20images/Backend-Architecture.png)

## Entity Relationship Diagram
![ERD](README%20images/Entity-Relationship-Diagram.png)

## Concepts Need to be Learned
1. Android Concepts = This includes lifecycles, activities, notifications, permissions, services, media store, intents, etc.
2. Jetpack Compose Concepts = States, effect handlers, etc., how to build user interface
3. Programming Language Concepts = Basics (Loops, Variables, Conditions, etc.) to Advance (Interface, Generics, Closures, etc.). In kotlin you need to learn how coroutines work. In python you might need to know list comprehensions. Functional Programming is highly recommended to be learned.
4. Flask Concepts = How to add routes. How to abstract the routes. Add wrapper for routes.
5. Room database = Query, Insert, Update, Delete records. Make entities, daos, database, and converters.
6. Dependency Injection.
7. Authorization = You should know how to authorize users. Unauthorized users should not be able to access data that requires authorization.
8. Security = You should always hash passwords. Always add validation when there are data needed to be changed, that requires some range or formats or specific user only can make the change. Validation to both client and server side are always good practice. Should add authorization to routes that need it. Do not pass sensitive information in frontend like passwords or codes (in forgot password).
9. Data consistency = When doing multiple write to database always make sure to add transactions, failures of next writes will cancel all writes. Make sure disable buttons temporarily that doing changes in backend database and delays to avoid multiple backend requests (can cause data inconsistencies).
10. SQLAlchemy
11. Navigation
12. Processing Images
13. Proto Datastore
14. HTTP Requests (How frontend and backend communication works)
15. Push Notifications
16. Database Design, Entity/Model Relationships Design.