from datetime import datetime
from datetime import timedelta
from datetime import date
from flask import Flask
from flask import render_template
from flask import request
from flask import redirect
from flask import url_for
from flask import session
from flask import flash
import mysql.connector
import connect
import smtplib
from email.message import EmailMessage
from flask import session


connection = None
dbconn = None

app = Flask(__name__)

app.config['SECRET_KEY'] = 'GROUP9'


def getCursor():
    global dbconn
    global connection
    if dbconn == None:
        connection = mysql.connector.connect(user=connect.dbuser,
                                             password=connect.dbpass, host=connect.dbhost,
                                             database=connect.dbname, port=connect.dbport, autocommit=True, connect_timeout=120)
        dbconn = connection.cursor()
        return dbconn
    else:
        return dbconn

#render template for pricing information
@app.route("/pricing/", methods=["GET"])
def price():
    return render_template("pricing_index.html")

#render template for general information for the fitness
@app.route("/aboutus/", methods=["GET"])
def aboutus():
    return render_template("aboutus.html")

#render template for group classes information and specialised classes infromation 
@app.route("/features/", methods=["GET"])
def features():
    return render_template("features.html")

# Peter, login, register, updating member part

@app.route("/", methods=["POST", "GET"])
def index():
    return render_template('index1.html')


@app.route("/login/", methods=["POST", "GET"])
def login():
    # Output message if something goes wrong...
    message = ''
    # Check if "userid" and "password" POST requests exist (user submitted form)
    if request.method == 'POST':
        userid = request.form.get('userid')
        print(userid)
        cur = getCursor()
        cur.execute("SELECT * FROM user WHERE userid = %s;", (userid,))
        check_user = cur.fetchone()
        print(check_user)
        if check_user:
            # allow render_template to the user home page
            roles = check_user[2]
            print(roles)
            session['userid'] = check_user[1]
            session['usertype'] = roles
            # allow manager to login
            if roles == 'admin':
                return render_template('manager_homepage.html',)
            # allow trainer to login

            elif roles == 'trainer':
                cur.execute(
                    "SELECT trainer_id FROM trainer WHERE userid = %s;", (check_user[0],))
                trainer_id = cur.fetchone()[0]
                session['trainer_id'] = trainer_id
                session['userid'] = check_user[0]
                session['trainer'] = check_user
                return redirect('/trainer/profile')
            # allow member to login
            else:
                cur.execute(
                    "SELECT member_id FROM member WHERE userid = %s;", (check_user[0],))

                row = cur.fetchone()
                if row:
                    member_id = row[0]
                    session['member_id'] = member_id
                    session['userid'] = check_user[0]
                    session['member'] = check_user
                    return redirect("/profile")
                #pop up message for wrong login 
                else:
                    message = 'User does not exist!'
                    return render_template('login.html', message=message)
        else:
            message = 'User does not exist!'
            return render_template('login.html', message=message)

    else:
        return render_template('login.html')

    # allow render_template to the register page

@app.route("/login/register", methods=["POST", "GET"])
def register():
    # Output message if something goes wrong...
    msg = ''
    # Check if "userid", "password" and "email" POST requests exist (user submitted form)
    if request.method == 'POST':
        # Get the new member's details from the form
        firstname = request.form['firstname']
        lastname = request.form['lastname']
        mobile = request.form['mobile']
        email = request.form['email']
        street = request.form['street']
        suburb = request.form['suburb']
        city = request.form['city']
        postalcode = request.form['postalcode']
        subscription_status = 0
        username = firstname + lastname
        roles = "member"

        # Get the current date and time and set as join date
        join_date = datetime.now().strftime('%Y-%m-%d')

        cur = getCursor()

        # Check for duplicate email addresses in the member table
        cur.execute("SELECT * FROM member WHERE email = %s", (email,))
        existing_member = cur.fetchone()

        if existing_member:
            # If a duplicate email is found, return an error message
            return render_template('register.html', msg='A member with this email address already exists.')

        cur.execute(
            "INSERT INTO user (username, roles) VALUES (%s, %s)", (username, roles))
        cur.execute("SELECT LAST_INSERT_ID()")
        userid = cur.fetchone()[0]

        sql = ("INSERT INTO member (firstname, lastname, mobile, email, street, suburb, city, postalcode, subscription_status, userid, join_date) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)")
        val = (firstname, lastname, mobile, email, street, suburb,
               city, postalcode, subscription_status, userid, join_date)

        cur.execute(sql, val)
        cur.execute("SELECT LAST_INSERT_ID()")
        member_id = cur.fetchone()[0]

        # Send confirmation email to the new member
        email_subject = 'Welcome to the Lincoln Fitness!'
        email_body = f"""Dear {firstname} {lastname},

    Welcome to Lincoln Fitness! Your membership has been successfully created.

    Membership Number: {userid}
    Join Date: {join_date}
    
    We look forward to seeing you at the gym!

    Best regards,
    Manager 
    Lincoln Fitness
    """
        send_email(email, email_subject, email_body)

        return render_template('new_member_confirmation.html',  firstname=firstname,
                               lastname=lastname,
                               email=email,
                               street=street,
                               suburb=suburb,
                               city=city,
                               postalcode=postalcode,
                               mobile=mobile,
                               userid=userid,
                               join_date=join_date)
    else:
        return render_template('register.html')

        # allow render_template to update the member information

@app.route("/login/admin/updatemember", methods=['GET', 'POST'])
def updatemember():

    if request.method == 'POST':
        userid = request.form.get('userid')
        print(f"User ID: {userid}")
        firstname = request.form.get('firstname')
        lastname = request.form.get('lastname')
        email = request.form.get('email')
        mobile = request.form.get('mobile')
        street = request.form.get('street')
        suburb = request.form.get('mobile')
        city = request.form.get('city')
        postalcode = request.form.get('postalcode')
        subscription_status = request.form.get('subscription_status')
        join_date = request.form.get('join_date')
        cur = getCursor()
        cur.execute("UPDATE member SET firstname=%s, lastname=%s, mobile=%s, email=%s, street=%s, suburb=%s, city=%s, postalcode=%s, subscription_status=%s, join_date=%s where userid=%s;",
                    (firstname, lastname, mobile, email, str(userid), street, suburb, city, postalcode, subscription_status, join_date,))
        cur.execute("select firstname, lastname, email, mobile, userid, street, suburb, city, postalcode, subscription_status, join_date from member where userid=%s;", (str(userid),))
        select_result = cur.fetchall()
        print(select_result)
        column_names = [desc[0] for desc in cur.description]
        print(f"{column_names}")
        return render_template('search_results.html ', dbresult=select_result, dbcols=column_names)
    else:
        userid = request.form.get('userid')
        if userid == '':
            return redirect("/login")
        else:
            print(request.args)
            userid = request.args.get('userid')
            cur = getCursor()
            cur.execute("SELECT * FROM member where userid=%s;",
                        (str(userid),))
            select_result = cur.fetchone()
            print(select_result)
            return render_template('updatemember.html', customer=select_result)

# allow render_template to new member

@app.route("/new_member")
def newmember():
    return render_template("new_member.html")

    # allow render_template to welcome page for manager

@app.route("/manager_homepage")
def manager_homepage():

    return render_template("manager_homepage.html")

# Send a email function


def send_email(to, subject, body):
    your_email = 'patrick.yeung@live.com'
    your_password = 'rvcznlpirmkdossh'

    msg = EmailMessage()
    msg.set_content(body)
    msg['Subject'] = subject
    msg['From'] = your_email
    msg['To'] = to

    server = smtplib.SMTP('smtp.office365.com', 587)
    server.ehlo()
    server.starttls()
    server.ehlo()
    server.login(your_email, your_password)
    server.send_message(msg)
    server.quit()


@app.route('/send_email_form', methods=['POST'])
def send_email_form():
    message = ''
    to = request.form['to']
    subject = request.form['subject']
    body = request.form['body']

    send_email(to, subject, body)

    return render_template("search_members.html", message='Email sent successfully!')

# Adding a new member


@app.route('/new_member', methods=["POST"])
def new_member():
    if request.method == 'POST':

        firstname = request.form['firstname']
        lastname = request.form['lastname']
        mobile = request.form['mobile']
        email = request.form['email']
        street = request.form['street']
        suburb = request.form['suburb']
        city = request.form['city']
        postalcode = request.form['postalcode']
        subscription_status = 0
        username = firstname + lastname
        roles = "member"

        join_date = datetime.now().strftime('%Y-%m-%d')

        cur = getCursor()

        # Check for duplicate email addresses in the member table
        cur.execute("SELECT * FROM member WHERE email = %s", (email,))
        existing_member = cur.fetchone()

        if existing_member:
            # If a duplicate email is found, return an error message
            return render_template('new_member.html', msg='A member with this email address already exists.')

        cur.execute(
            "INSERT INTO user (username, roles) VALUES (%s, %s)", (username, roles))
        cur.execute("SELECT LAST_INSERT_ID()")
        userid = cur.fetchone()[0]

        sql = ("INSERT INTO member (firstname, lastname, mobile, email, street, suburb, city, postalcode, subscription_status, userid, join_date) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)")
        val = (firstname, lastname, mobile, email, street, suburb,
               city, postalcode, subscription_status, userid, join_date)

        cur.execute(sql, val)
        cur.execute("SELECT LAST_INSERT_ID()")
        member_id = cur.fetchone()[0]

        # Send confirmation email to the new member
        email_subject = 'Welcome to the Lincoln Fitness!'
        email_body = f"""Dear {firstname} {lastname},
 
Welcome to Lincoln Fitness! Your membership has been successfully created.
 
Membership Number: {userid}
Join Date: {join_date}
       
Please click this link to complete your payment.
 
We look forward to seeing you at the gym!
 
Best regards,
Manager
Lincoln Fitness
        """
        send_email(email, email_subject, email_body)

        return render_template('new_member.html', msg=f"{firstname} {lastname} has been successfully added to the system! The member should have received a confirmation email.")


# Searching a member
@app.route('/search_members', methods=["GET", "POST"])
def search_members():
    if request.method == "POST":
        search_query = request.form['search_query']
        cur = getCursor()
        if search_query.strip() == "":
            sql = """SELECT 
                    m.userid, m.firstname, m.lastname, m.mobile, m.email, m.street, m.suburb, m.city, m.postalcode,
                    CASE 
                        WHEN m.subscription_status = 1 THEN 'Monthly'
                        ELSE 'Not Subscribed'
                    END as Subscription,
                    CASE 
                        WHEN m.subscription_status = 1 THEN DATEDIFF(DATE_ADD(ms.payment_date, INTERVAL 30 DAY), NOW())
                        ELSE NULL
                    END as DaysLeft,
                    m.member_id
                FROM member m
                LEFT JOIN membership ms ON m.member_id = ms.member_id;
                """
            cur.execute(sql)
            members = cur.fetchall()
            return render_template("search_results.html", members=members)
        else:
            sql = """SELECT 
                    m.userid, m.firstname, m.lastname, m.mobile, m.email, m.street, m.suburb, m.city, m.postalcode,
                    CASE 
                        WHEN m.subscription_status = 1 THEN 'Monthly'
                        ELSE 'Not Subscribed'
                    END as Subscription,
                    CASE 
                        WHEN m.subscription_status = 1 THEN DATEDIFF(DATE_ADD(ms.payment_date, INTERVAL 30 DAY), NOW())
                        ELSE NULL
                    END as DaysLeft,
                    m.member_id
                FROM member m
                LEFT JOIN membership ms ON m.member_id = ms.member_id
                WHERE userid LIKE %s OR firstname LIKE %s OR lastname LIKE %s;"""
            query = '%' + search_query + '%'
            val = (query, query, query)
            cur.execute(sql, val)
            members = cur.fetchall()
            return render_template("search_results.html", members=members)
    return render_template("search_members.html")

# Deleting a member


@app.route('/delete_member', methods=["POST"])
def delete_member():
    message = ''
    member_id = request.form['member_id']
    cur = getCursor()

    # Delete related rows in the attendance table
    sql_attendance_delete = "DELETE FROM attendance WHERE member_id = %s"
    val_attendance_delete = (member_id,)
    cur.execute(sql_attendance_delete, val_attendance_delete)

    # Delete related rows in the payment table
    sql_payment_delete = """DELETE payment
                            FROM payment
                            JOIN specializedclass_booking ON payment.specializedclass_bookingid = specializedclass_booking.specializedclass_bookingid
                            WHERE specializedclass_booking.member_id = %s"""
    val_payment_delete = (member_id,)
    cur.execute(sql_payment_delete, val_payment_delete)

    # Delete related rows in the groupclass_booking table
    sql_groupclass_delete = "DELETE FROM groupclass_booking WHERE member_id = %s"
    val_groupclass_delete = (member_id,)
    cur.execute(sql_groupclass_delete, val_groupclass_delete)

    # Delete related rows in the specializedclass_booking table
    sql_specialized_delete = "DELETE FROM specializedclass_booking WHERE member_id = %s"
    val_specialized_delete = (member_id,)
    cur.execute(sql_specialized_delete, val_specialized_delete)

    # Finally, delete the member
    sql_member = "DELETE FROM member WHERE member_id = %s"
    val_member = (member_id,)
    cur.execute(sql_member, val_member)

    return render_template('search_members.html', message='Member has been deleted!')

    # allow render_template to view the list of trainer

@app.route('/admin/trainers')
def list_trainers():
    cur = getCursor()
    sql = """SELECT trainer_id, first_name, last_name, email, mobile, speciality, userid
             FROM trainer"""
    cur.execute(sql)
    trainers = cur.fetchall()
    return render_template("trainers_list.html", trainers=trainers)


# Below is Alyssa's code
@app.route('/trainer')
def trainerhome():
    # session['trainer'] = 1009
    userid = session.get('trainer')

    # connect database
    cur = getCursor()
    # run sql get all data from trainer
    specilized_course_sql = """select specializedclasses.specializedclasses_id,class_type, class_desc,specializedclass_sessionid,specializedclass_time,specializedclass_date
from specializedclasses join trainer on trainer.trainer_id =specializedclasses.trainer_id
join specializedclass_session on specializedclasses.specializedclasses_id=specializedclass_session.specializedclasses_id 
where trainer.trainer_id=%s
and specializedclass_time>now() order by specializedclass_time;"""
    trainer_id = (userid,)
    cur.execute(specilized_course_sql, trainer_id)
    specilized_course_trainer_classes = cur.fetchall()

    group_course_sql = """select  groupclasses.groupclasses_id,classname,class_description,session_id,class_time,class_capacity from groupclasses join trainer on groupclasses.trainer_id=trainer.trainer_id
join groupclasses_session on groupclasses.groupclasses_id=groupclasses_session.groupclasses_id
where trainer.trainer_id=%s and class_time >now() order by class_time;     
    """
    cur.execute(group_course_sql, trainer_id)
    group_course_trainer_classes = cur.fetchall()

    return render_template('trainer_home.html', specilized_course_trainer_classes=specilized_course_trainer_classes, group_course_trainer_classes=group_course_trainer_classes)

# Trainer upcoming appointments


@app.route("/trainer/specialappointments", methods=["GET"])
def specialappointments_get():
    return render_template("trainerspecialappoinments.html", sessionlist=[])

            # serach for the trainer course

@app.route("/trainer/specialappointments", methods=["POST"])
def specialappointments():
    if request.method == "POST":
        search = request.form["Search"]
        value = request.form["value"]
        connection = getCursor()

    if search == "firstname":
        searchmember = "%" + value + "%"
        sql = """select m.member_id, m.firstname, s.specializedclass_time, s.specializedclass_date, s.specializedclasses_id, sc.class_type from member m
 JOIN specializedclass_booking sb ON m.member_id = sb.member_id
 join specializedclass_session s on sb.specializedclass_sessionid= s.specializedclass_sessionid
 JOIN specializedclasses sc ON s.specializedclasses_id = sc.specializedclasses_id
 WHERE s.specializedclass_date> NOW() AND m.firstname LIKE %s;"""
        connection.execute(sql, (searchmember,))

    elif search == "class_type":
        searchmember = "%" + value + "%"
        sql = """select m.member_id, m.firstname, s.specializedclass_time, s.specializedclass_date, s.specializedclasses_id, sc.class_type from member m
 JOIN specializedclass_booking sb ON m.member_id = sb.member_id
 join specializedclass_session s on sb.specializedclass_sessionid= s.specializedclass_sessionid
 JOIN specializedclasses sc ON s.specializedclasses_id = sc.specializedclasses_id
 WHERE s.specializedclass_date> NOW() AND sc.class_type LIKE %s;"""
        connection.execute(sql, (searchmember,))
    else:
        sql = """select m.member_id, m.firstname, s.specializedclass_time, s.specializedclass_date, s.specializedclasses_id, sc.class_type from member m
 JOIN specializedclass_booking sb ON m.member_id = sb.member_id
 join specializedclass_session s on sb.specializedclass_sessionid= s.specializedclass_sessionid
 JOIN specializedclasses sc ON s.specializedclasses_id = sc.specializedclasses_id
 WHERE s.specializedclass_date> NOW() AND m.firstname LIKE %s AND sc.class_type LIKE %s;"""
        connection.execute(sql, (searchmember, searchmember,))

    sessionList = connection.fetchall()
    print(sessionList)
    return render_template("trainerspecialappoinments.html", sessionlist=sessionList)

        # allow render_template to  trainer group appointments

@app.route("/trainer/groupappointments", methods=["GET"])
def groupappointments_get():
    return render_template("trainergroupappointments.html", grouplist=[])

        # trainer view the group appointments

@app.route("/trainer/groupappointments", methods=["POST"])
def groupappointments():
    if request.method == "POST":
        search = request.form["Search"]
        value = request.form["value"]
        connection = getCursor()

    if search == "firstname":
        searchmember = "%" + value + "%"
        sql = """ select m.member_id, m.firstname, gs.class_time, gs.class_date, g.groupclasses_id, g.classname from member m
        JOIN groupclass_booking gb ON m.member_id = gb.member_id
        join groupclasses_session gs on gb.session_id= gs.session_id
        JOIN groupclasses g ON gs.groupclasses_id = g.groupclasses_id
        WHERE gs.class_date > NOW() AND m.firstname LIKE %s;"""
        connection.execute(sql, (searchmember,))

    elif search == "classname":
        searchmember = "%" + value + "%"
        sql = """ select m.member_id, m.firstname, gs.class_time, gs.class_date, g.groupclasses_id, g.classname from member m
                JOIN groupclass_booking gb ON m.member_id = gb.member_id
                    join groupclasses_session gs on gb.session_id= gs.session_id
                    JOIN groupclasses g ON gs.groupclasses_id = g.groupclasses_id
                    WHERE gs.class_date > NOW() AND g.classname LIKE %s;"""
        connection.execute(sql, (searchmember,))
    else:
        sql = """ select m.member_id, m.firstname, gs.class_time, gs.class_date, g.groupclasses_id, g.classname from member m
                JOIN groupclass_booking gb ON m.member_id = gb.member_id
                 join groupclasses_session gs on gb.session_id= gs.session_id
                JOIN groupclasses g ON gs.groupclasses_id = g.groupclasses_id
                WHERE gs.class_date > NOW() AND m.firstname LIKE %s AND g.classname %s;"""
        connection.execute(sql, (searchmember, searchmember,))

    groupList = connection.fetchall()
    print(groupList)
    return render_template("trainergroupappointments.html", grouplist=groupList)


##### Its not working so I am replacing with other code######
# @app.route('/trainer/course_members', methods=["GET","POST"])
# def mycourses():
    # userid = session.get('userid')
    # get course session id

    # group_course_session_ID = request.args.get("group_course_session_id")
    # specilized_course_session_id = request.args.get("specilized_course_session_id")

    # get group course specific session  members
    # if(group_course_session_ID != None):
    # connect database
    # cur = getCursor()

    # group_course_member_sql = """select groupclasses_session.session_id,member.member_id,class_time,firstname,lastname,mobile,email,street,suburb,city,postalcode,join_date,subscription_status from  groupclass_booking join groupclasses_session
    # on groupclasses_session.session_id=groupclass_booking.session_id
    # join member on groupclass_booking.member_id=member.member_id where groupclasses_session.session_id=%s; """
    # session_id = (group_course_session_ID,)
    # cur.execute(group_course_member_sql, session_id)
    # group_course_member_list = cur.fetchall()

    # return render_template('trainer_course_member_list.html', group_course_member_list=group_course_member_list, course_session_ID=group_course_session_ID)
    # elif(specilized_course_session_id != None):

    # connect database
    # cur = getCursor()
    # specilized_course_member_sql = """select specializedclass_booking.specializedclass_sessionid,member.member_id,specializedclass_time, firstname, lastname,mobile,email,street,suburb,city,postalcode,join_date,subscription_status
    # from specializedclass_booking join specializedclass_session
    # on specializedclass_booking.specializedclass_sessionid=specializedclass_session.specializedclass_sessionid
    #   join member on specializedclass_booking.member_id=member.member_id where  specializedclass_booking.specializedclass_sessionid=%s;
    # """
    # session_id = (specilized_course_session_id,)
    # cur.execute(specilized_course_member_sql, session_id)
    # specilized_course_member_list = cur.fetchall()
    # return render_template('trainer_course_member_list.html', specilized_course_member_list=specilized_course_member_list, course_session_ID=specilized_course_session_id)


@app.route('/trainer/addsessioncoursemember', methods=["POST", "GET"])
def add_sessioncourse_member():
    if request.method == 'GET':
        group_course_session_ID = request.args.get("group_course_sessionid")
        specilized_course_session_ID = request.args.get(
            "specilized_course_sessionid")

        if (group_course_session_ID != None):
            # get all members
            cur = getCursor()
            sql = """
            SELECT member_id,firstname,lastname FROM member where member_id not in (select member.member_id from  groupclass_booking join groupclasses_session 
                on groupclasses_session.session_id=groupclass_booking.session_id
                    join member on groupclass_booking.member_id=member.member_id where groupclasses_session.session_id=%s);
            """
            session_id = (group_course_session_ID,)
            cur.execute(sql, session_id)
            remaining_member_list = cur.fetchall()

            return render_template('trainer_add_member_to_course.html', group_course_session_ID=group_course_session_ID, remaining_member_list=remaining_member_list)

        if (specilized_course_session_ID != None):
            # get all members
            cur = getCursor()
            sql = """
           SELECT member_id,firstname,lastname FROM member where member_id not in  (select member.member_id
          from specializedclass_booking join specializedclass_session 
             on specializedclass_booking.specializedclass_sessionid=specializedclass_session.specializedclass_sessionid
                     join member on specializedclass_booking.member_id=member.member_id where specializedclass_booking.specializedclass_sessionid=%s);
            """
            session_id = (specilized_course_session_ID,)
            cur.execute(sql, session_id)
            remaining_member_list = cur.fetchall()
            return render_template('trainer_add_member_to_course.html', specilized_course_session_ID=specilized_course_session_ID, remaining_member_list=remaining_member_list)

    else:
        # when post method
        group_course_session_ID = request.args.get("group_course_session_ID")
        specilized_course_session_id = request.args.get(
            "specilized_course_session_ID")
        member_id = request.form['dropdown']
        member_id = int(member_id)

        # get group course specific session  members
        if (group_course_session_ID != None):

            # connect database
            cur = getCursor()

            # insert data sql
            cur.execute("INSERT INTO `groupclass_booking` (`session_id`, `member_id`) VALUES (%s, %s);",
                        (group_course_session_ID, member_id))

            # display all members in the session id
            group_course_member_sql = """select groupclasses_session.session_id,member.member_id,class_time,firstname,lastname,mobile,email,street,suburb,city,postalcode,join_date,subscription_status from  groupclass_booking join groupclasses_session 
                    on groupclasses_session.session_id=groupclass_booking.session_id
                    join member on groupclass_booking.member_id=member.member_id where groupclasses_session.session_id=%s; """
            session_id = (group_course_session_ID,)
            cur.execute(group_course_member_sql, session_id)
            group_course_member_list = cur.fetchall()

            return render_template('trainer_course_member_list.html', group_course_member_list=group_course_member_list, course_session_ID=group_course_session_ID)

        elif (specilized_course_session_id != None):

            # connect database
            cur = getCursor()

            # insert data sql
            cur.execute("INSERT INTO `specializedclass_booking` (`specializedclass_sessionid`, `member_id`) VALUES (%s, %s);",
                        (specilized_course_session_id, member_id,))

            # display all members in the session id

            specilized_course_member_sql = """select specializedclass_booking.specializedclass_sessionid,member.member_id,specializedclass_time, firstname, lastname,mobile,email,street,suburb,city,postalcode, join_date,subscription_status 
                from specializedclass_booking join specializedclass_session 
                on specializedclass_booking.specializedclass_sessionid=specializedclass_session.specializedclass_sessionid
                    join member on specializedclass_booking.member_id=member.member_id where  specializedclass_booking.specializedclass_sessionid=%s;
                """
            session_id = (specilized_course_session_id,)
            cur.execute(specilized_course_member_sql, session_id)
            specilized_course_member_list = cur.fetchall()
            return render_template('trainer_course_member_list.html', specilized_course_member_list=specilized_course_member_list, course_session_ID=specilized_course_session_id)

#trainer delete seesion course members
@app.route('/trainer/deletesessioncoursemember')
def delete_sessioncourse_member():

    group_course_session_ID = request.args.get("group_course_session_id")
    specilized_course_session_id = request.args.get(
        "specilized_course_session_id")

    member_id = request.args.get("memberid")
    member_id = int(member_id)

    # get group course specific session  members
    if (group_course_session_ID != None):

        # connect database
        cur = getCursor()
        # find the correct booking_id

        cur.execute("select groupclass_bookingid from groupclass_booking where session_id=%s and member_id=%s;",
                    (group_course_session_ID, member_id,))
        booking_id_list = cur.fetchall()
        booking_id = booking_id_list[0][0]

        # delete  booking id row
        cur.execute(
            "DELETE FROM `groupclass_booking` WHERE (`groupclass_bookingid` = %s);", (booking_id,))

        # display all members in the session id
        group_course_member_sql = """select groupclasses_session.session_id,member.member_id,class_time,firstname,lastname,mobile,email,street,suburb,city,postalcode,join_date,subscription_status  from  groupclass_booking join groupclasses_session 
                    on groupclasses_session.session_id=groupclass_booking.session_id
                    join member on groupclass_booking.member_id=member.member_id where groupclasses_session.session_id=%s; """
        session_id = (group_course_session_ID,)
        cur.execute(group_course_member_sql, session_id)
        group_course_member_list = cur.fetchall()

        return render_template('trainer_course_member_list.html', group_course_member_list=group_course_member_list, course_session_ID=group_course_session_ID)

    elif (specilized_course_session_id != None):

        # connect database
        cur = getCursor()
        cur.execute("select specializedclass_bookingid from specializedclass_booking where specializedclass_sessionid=%s and member_id=%s;",
                    (specilized_course_session_id, member_id,))
        booking_id_list = cur.fetchall()
        booking_id = booking_id_list[0][0]

        # delete  booking id row
        cur.execute(
            "DELETE FROM `specializedclass_booking` WHERE (`specializedclass_bookingid` = %s);", (booking_id,))

        # display all members in the session id

        specilized_course_member_sql = """select specializedclass_booking.specializedclass_sessionid,member.member_id,specializedclass_time, firstname, lastname,mobile,email,street,suburb,city,postalcode,join_date,subscription_status
                from specializedclass_booking join specializedclass_session 
                on specializedclass_booking.specializedclass_sessionid=specializedclass_session.specializedclass_sessionid
                    join member on specializedclass_booking.member_id=member.member_id where  specializedclass_booking.specializedclass_sessionid=%s;
                """
        session_id = (specilized_course_session_id,)
        cur.execute(specilized_course_member_sql, session_id)
        specilized_course_member_list = cur.fetchall()
        return render_template('trainer_course_member_list.html', specilized_course_member_list=specilized_course_member_list, course_session_ID=specilized_course_session_id)


# upcoming course search by id or email
@app.route('/trainer_search_appointment', methods=["POST"])
def trainer_search_appointment():
    if request.method == "POST":

        # get course session id

        group_course_session_ID = request.args.get("group_course_session_ID")
        specilized_course_session_id = request.args.get(
            "specilized_course_session_ID")
        search_query = request.form['search']
        search_query = "%"+search_query+"%"

        # get group course specific session  members
    if (group_course_session_ID != None):

        # connect database
        cur = getCursor()

        # like  sql
        group_course_member_sql = """select groupclasses_session.session_id,member.member_id,class_time,firstname,lastname,mobile,email,street,suburb,city,postalcode,join_date,subscription_status from  groupclass_booking join groupclasses_session 
               on groupclasses_session.session_id=groupclass_booking.session_id
               join member on groupclass_booking.member_id=member.member_id where groupclasses_session.session_id=%s and (email like %s  or member.member_id like %s); """
        val = (group_course_session_ID, search_query, search_query,)

        cur.execute(group_course_member_sql, val)
        group_course_member_list = cur.fetchall()

        return render_template('trainer_course_member_list.html', group_course_member_list=group_course_member_list, course_session_ID=group_course_session_ID)

    elif (specilized_course_session_id != None):
        cur = getCursor()
        sql = """select specializedclass_booking.specializedclass_sessionid,member.member_id,specializedclass_time, firstname, lastname,mobile,email,street,suburb,city,postalcode,join_date,subscription_status 
        from specializedclass_booking join specializedclass_session 
       on specializedclass_booking.specializedclass_sessionid=specializedclass_session.specializedclass_sessionid
        join member on specializedclass_booking.member_id=member.member_id where  specializedclass_booking.specializedclass_sessionid=%s and (email like %s  or member.member_id like %s);"""

        val = (specilized_course_session_id, search_query, search_query,)

        cur.execute(sql, val)
        specilized_course_member_list = cur.fetchall()

        return render_template("trainer_course_member_list.html", specilized_course_member_list=specilized_course_member_list, course_session_id=specilized_course_session_id)


# trainer view his or her profile
@app.route('/trainer/profile', methods=["GET"])
def trainerprofile():
    # session['trainer'] = 1001
    userid = session.get("userid")

    # connect database
    cur = getCursor()
    # run sql get all data for trainer's appointments

    cur.execute("SELECT * FROM trainer where userid=%s;", (userid,))
    # trainer_id = (userid,)
    # cur.execute(sql, trainer_id)
    trainerprofile = cur.fetchone()
    print(trainerprofile)
    return render_template('trainerprofile1.html', trainerprofile=trainerprofile)


@app.route("/traineredit/<int:userid>", methods=["GET", "POST"])
def traineredit(userid):
    if request.method == "GET":
        connection = getCursor()
        connection.execute(
            "Select * from trainer WHERE userid = %s;", (userid,))
        trainerprofile = connection.fetchone()
        print(trainerprofile)
        return render_template("trainer_modifyprofile.html", trainerprofile=trainerprofile, userid=userid)


# trainer modifies his or her profile
@app.route("/trainer/modifyprofile/", methods=["POST", "GET"])
def trainermodifyprofile():
    # session['trainer'] = 1001
    # trainer_id = session.get('trainer')

    if request.method == "POST":
        # trainer_id = request.form['trainer_id']
        first_name = request.form['first_name']
        last_name = request.form['last_name']
        email = request.form['email']
        mobile = request.form['mobile']
        speciality = request.form['speciality']
        userid = request.form['userid']

        # connect database
        cur = getCursor()

        # run sql update trainer's profile
        cur.execute("UPDATE trainer SET first_name=%s,last_name=%s,email=%s,mobile=%s,speciality=%s where userid=%s;", (
            first_name, last_name, email, mobile, speciality, userid,))
        return redirect('/trainer/profile')

    # else:
        # session['trainer'] = 1001
        # trainer_id = session.get('trainer')

        # connect database
        # cur = getCursor()
        # cur.execute(
        # """select * from trainer where trainer.trainer_id=%s;""", (trainer_id,))
        # trainerdetails = cur.fetchone()
       # return render_template('trainer_modifyprofile.html', trainerdetails=trainerdetails)


@app.route('/loginout', methods=['POST', "GET"])
def loginout():
    session.clear()
    return redirect('/')


#### Simran's Coding starts here#####


# @app.route("/login")
# def memberlog():
    # return render_template("login2.html")

# @app.route("/login")
# def memberlog():
   # return render_template("login.html")

 # allow render_template to specialized class table
@app.route("/specializedclasstable")
def table():
    return render_template("specializedclasstable.html")


# @app.route("/login", methods=["GET", "POST"])
# def memberlogin():
    # if request.method == 'POST':
    # userid = request.form["userid"]
    # connection = getCursor()
    # connection.execute("SELECT * from member WHERE userid= %s;", (userid,))
    # member = connection.fetchone()
    # if member:
    # session['userid'] = member[10]
    # session['member'] = member
    # return redirect("/profile")
    # else:
    # error_message = "Invalid Credentials"
    # return render_template("login2.html", error_message=error_message)

#render the profile page for meber
@app.route("/profile")
def profile():
    if 'userid' in session and 'member' in session:
        print('111111111111111111111', session)
        userid = session.get("userid")
        connection = getCursor()
        connection.execute(
            "Select * from member WHERE userid = %s;", (userid,))
        member = connection.fetchone()
        print(member)
        return render_template("profile.html", member=member)
    else:
        return redirect("/login")

    # render the profile for trainer

@app.route("/trainer/profile/<int:member_id>", methods=["GET", "POST"])
def trapro(member_id):
    print(member_id)
    if request.method == "GET":
        connection = getCursor()
        connection.execute(
            "Select * from member WHERE member_id = %s;", (member_id,))
        member = connection.fetchone()
        return render_template("trapro.html", member=member, member_id=member_id)

# log out function 
@app.route("/logout")
def logout():
    session.pop('member', None)
    return redirect("/login")

#menager edit member information 
@app.route("/memberedit/<int:userid>", methods=["GET", "POST"])
def memberedit(userid):
    if request.method == "GET":
        # import pdb;pdb.set_trace()
        # userid = session.get('userid')
        connection = getCursor()
        connection.execute(
            "Select * from member WHERE userid = %s;", (userid,))
        member = connection.fetchone()
        print(member)
        return render_template("edit.html", member=member, userid=userid)


@app.route("/manageredit/<int:userid>", methods=["GET", "POST"])
def manageredit(userid):
    if request.method == "GET":
        # import pdb;pdb.set_trace()
        # userid = session.get('userid')
        connection = getCursor()
        connection.execute(
            "Select * from member WHERE userid = %s;", (userid,))
        member = connection.fetchone()
        print(member)
        return render_template("manageredit.html", member=member, userid=userid)

#upadte member information 
@app.route("/updatemember", methods=["POST"])
def updatemem():
    message = ''
    if request.method == "POST":
        # import pdb;pdb.set_trace()
        firstname = request.form["firstname"]
        lastname = request.form["lastname"]
        mobile = request.form["mobile"]
        email = request.form["email"]
        street = request.form["street"]
        suburb = request.form["suburb"]
        city = request.form["city"]
        postalcode = request.form["postalcode"]
        userid = request.form["userid"]
        cur = getCursor()
        cur.execute("UPDATE member SET firstname = %s, lastname = %s, mobile = %s, email = %s, street = %s, suburb = %s, city = %s, postalcode = %s WHERE userid = %s;",
                    (firstname, lastname, mobile, email, street, suburb, city, postalcode, userid,))
        connection.commit()
        return redirect("/profile")

#manager update member information
@app.route("/admin/updatemember", methods=["POST"])
def managerupdatemem():
    message = ''
    if request.method == "POST":
        # import pdb;pdb.set_trace()
        firstname = request.form["firstname"]
        lastname = request.form["lastname"]
        mobile = request.form["mobile"]
        email = request.form["email"]
        street = request.form["street"]
        suburb = request.form["suburb"]
        city = request.form["city"]
        postalcode = request.form["postalcode"]
        userid = request.form["userid"]
        cur = getCursor()
        cur.execute("UPDATE member SET firstname = %s, lastname = %s, mobile = %s, email = %s, street = %s, suburb = %s, city = %s, postalcode = %s WHERE userid = %s;",
                    (firstname, lastname, mobile, email, street, suburb, city, postalcode, userid,))
        connection.commit()
        return render_template('search_members.html', message=f'{firstname} {lastname}\'s details have been successfully updated!')

#trainer view a list of members
@app.route("/trainer/memberslist", methods=["GET"])
def tramemberslist():
    connection = getCursor()
    sql = """SELECT member_id, firstname, lastname, mobile, email, street, suburb, city, postalcode,join_date FROM member;"""
    connection.execute(sql)
    member = connection.fetchall()
    print(member)
    return render_template("tramemberslist.html", members=member)

#trainer view the trainersession 
@app.route("/admin/trainersession", methods=["GET"])
def trainersession_get():
    return render_template("groupclassadmin.html", trainerlist=[])

#manager view the trainer  session 
@app.route("/admin/trainersession", methods=["POST"])
def trainersession():
    if request.method == "POST":
        search = request.form["Search"]
        value = request.form["value"]
        connection = getCursor()

    if search == "first_name":
        searchtrainer = "%" + value + "%"
        sql = """select gs.session_id, gs.groupclasses_id, gs.class_time, g.classname, g.trainer_id, t.first_name from groupclasses_session gs
                    JOIN groupclasses g ON gs.groupclasses_id = g.groupclasses_id
                    JOIN trainer t ON g.trainer_id = t.trainer_id WHERE t.first_name LIKE %s;"""
        connection.execute(sql, (searchtrainer,))

    elif search == "classtime":
        searchtrainer = "%" + value + "%"
        sql = """select gs.session_id, gs.groupclasses_id, gs.class_time, g.classname, g.trainer_id, t.first_name
                    from groupclasses_session gs
                    JOIN groupclasses g ON gs.groupclasses_id = g.groupclasses_id
                    JOIN trainer t ON g.trainer_id = t.trainer_id WHERE gs.class_time LIKE %s;"""
        connection.execute(sql, (searchtrainer,))
    else:
        sql = """select gs.session_id, gs.groupclasses_id, gs.class_time, g.classname, g.trainer_id, t.first_name
                    from groupclasses_session gs
                    JOIN groupclasses g ON gs.groupclasses_id = g.groupclasses_id
                    JOIN trainer t ON g.trainer_id = t.trainer_id WHERE t.first_name LIKE %s OR gs.class_time LIKE %s;"""
        connection.execute(sql, (searchtrainer,))

    trainerList = connection.fetchall()
    print(trainerList)
    return render_template("groupclassadmin.html", trainerlist=trainerList)

#view the infoamtion for specialized classes
@app.route("/specializedclasses", methods=["GET"])
def specialclass():
    connection = getCursor()
    sql = """select sp.specializedclasses_id, sp.class_type, sp.class_desc, sp.trainer_id, sp.schedule, t.first_name from specializedclasses sp 
                        JOIN trainer t ON sp.trainer_id = t.trainer_id;"""
    connection.execute(sql)
    classes = connection.fetchall()
    print(classes)
    return render_template("specializedclasstable.html", classes=classes)

#view the information for group classes
@app.route("/groupclasses", methods=["GET"])
def groupclass():
    connection = getCursor()
    sql = """select gp.groupclasses_id, gp.classname, gp.class_description, gp.trainer_id, t.first_name from groupclasses gp 
         JOIN trainer t ON gp.trainer_id= t.trainer_id;"""
    connection.execute(sql)
    groups = connection.fetchall()
    print(groups)
    return render_template("groupclasses.html", groups=groups)

#view the information for group classes
@app.route("/groupclasses/session", methods=["GET"])
def groupsession1():
    connection = getCursor()
    sql = """select gs.session_id,gs.groupclasses_id,gs.class_time,gs.class_date,gs.class_capacity,g.classname, g.trainer_id, t.first_name
          from groupclasses_session gs 
          JOIN groupclasses g ON gs.groupclasses_id = g.groupclasses_id
          JOIN trainer t ON g.trainer_id = t.trainer_id;"""
    connection.execute(sql)
    sessiongroup = connection.fetchall()
    print(sessiongroup)
    return render_template("groupsession.html", sessiongroup=sessiongroup)

#make a booking for group classes
@app.route("/groupsession/add/<int:session_id>", methods=["GET", "POST"])
def bookgroup(session_id):
    connection = getCursor()
    if 'userid' not in session:
        print("Please log in first", "error")
        return redirect("/login")

    userid = session['member_id']
    sql = "INSERT INTO groupclass_booking(session_id, member_id) VALUES (%s,%s);"
    values = (session_id, userid)
    connection.execute(sql, values)

    sql = """UPDATE groupclasses_session g
        INNER JOIN groupclasses_session gs ON g.groupclasses_id = gs.groupclasses_id
        SET g.class_capacity = g.class_capacity - 1
        WHERE gs.session_id = %s;"""
    connection.execute(sql, (session_id,))
    print("Session booked successfully")
    return redirect("/groupbookingconfirmation")

#booking confirmation for group classes
@app.route("/groupbookingconfirmation")
def groupconfirmation():
    connection = getCursor()
    userid = session['member_id']

    sql = """SELECT gb.groupclass_bookingid, gp.session_id, g.classname, m.firstname from groupclass_booking gb
           JOIN member m ON gb.member_id = m.member_id
           JOIN groupclasses_session gp ON gb.session_id = gp.session_id
           JOIN groupclasses g ON gp.groupclasses_id = g.groupclasses_id
           WHERE m.member_id = %s;"""
    values = (userid,)
    connection.execute(sql, values)
    booking = connection.fetchall()
    return render_template("groupbookingconfirmation.html", booking=booking)


# specialized classes current bookings
@app.route("/currentbookings")
def currentbookings():
    connection = getCursor()
    sql = """ select sb.specializedclass_bookingid, sb.specializedclass_sessionid, sb.member_id, s.specializedclasses_id,
                    s.specializedclass_time, s.specializedclass_date, m.firstname, sp.class_type 
                from specializedclass_booking sb
                     JOIN specializedclass_session s ON sb.specializedclass_sessionid = s.specializedclass_sessionid
                JOIN member m ON sb.member_id = m.member_id
                JOIN specializedclasses sp ON s.specializedclasses_id= sp.specializedclasses_id
            order by m.member_id, m.firstname;"""
    connection.execute(sql)
    currentBooking = connection.fetchall()
    print(currentBooking)
    return render_template("currentbookings.html", currentbooking=currentBooking)

#view the booked classes
@app.route("/currentgroupbookings")
def currentgroupbookings():
    connection = getCursor()
    sql = """ select gp.groupclass_bookingid, gp.session_id, gp.member_id, gs.groupclasses_id,
                    gs.class_time, gs.class_date, m.firstname, g.classname 
                from groupclass_booking gp
                     JOIN groupclasses_session gs ON gp.session_id = gs.session_id
                JOIN member m ON gp.member_id = m.member_id
                JOIN groupclasses g ON gs.groupclasses_id= g.groupclasses_id
            order by m.member_id, m.firstname;"""
    connection.execute(sql)
    currentgroupBooking = connection.fetchall()
    print(currentgroupBooking)
    return render_template("currentgroupbookings.html", currentgroupbooking=currentgroupBooking)

#view the list for popular classes
@app.route("/popularclasses")
def popularclasses():
    connection = getCursor()
    sql = """SELECT s.class_type, COUNT(specializedclass_bookingid) as totalcount_bookings 
    from specializedclasses s 
    LEFT JOIN specializedclass_session ss ON s.specializedclasses_id = ss.specializedclasses_id 
    LEFT JOIN specializedclass_booking sb ON ss.specializedclass_sessionid = sb.specializedclass_sessionid
         GROUP BY s.specializedclasses_id;"""
    connection.execute(sql)
    popularclasses = connection.fetchall()
    print(popularclasses)
    return render_template("popularclasses.html", popularclasses=popularclasses)

# member view the list for popular classes

@app.route("/member/session", methods=["GET"])
def membersession():
    connection = getCursor()
    sql = """select s.specializedclasses_id, s.specializedclass_sessionid, s.specializedclass_time, s.specializedclass_date,
          sc.trainer_id,sc.class_type, sc.pricing from specializedclass_session s JOIN specializedclasses sc ON s.specializedclasses_id = sc.specializedclasses_id;"""
    connection.execute(sql)
    sessionlist = connection.fetchall()
    print(sessionlist)
    return render_template("membersession.html", sessionlist=sessionlist)

#member view the list for specialised classes

@app.route("/membersession/add/<int:specializedclass_sessionid>", methods=["GET", "POST"])
def bookform(specializedclass_sessionid):
    connection = getCursor()
    if 'userid' not in session:
        print("Please log in first", "error")
        return redirect("/login")

    userid = session['member_id']
    sql = "INSERT INTO specializedclass_booking(specializedclass_sessionid, member_id) VALUES (%s,%s);"
    values = (specializedclass_sessionid, userid)
    print(values)
    connection.execute(sql, values)
    print("Session booked successfully", "success")
    return redirect("/bookingconfirmation")

#member view the booking confirmation

@app.route("/bookingconfirmation")
def bookingconfirmation():
    connection = getCursor()
    userid = session['member_id']
    sql = """Select sb.specializedclass_bookingid, ss.specializedclass_sessionid, s.pricing, s.class_type, m.firstname from specializedclass_booking sb
        JOIN member m ON sb.member_id = m.member_id
JOIN specializedclass_session ss ON sb.specializedclass_sessionid = ss.specializedclass_sessionid
JOIN specializedclasses s ON ss.specializedclasses_id = s.specializedclasses_id
WHERE m.member_id = %s;"""
    values = (userid,)
    connection.execute(sql, values)
    bookings = connection.fetchall()
    return render_template("bookingconfirmation.html", bookings=bookings)


# confirmation route for Specialized Class booking
@app.route("/payment_confirmation/<int:specializedclass_bookingid>", methods=["GET", "POST"])
def payment_confirmation(specializedclass_bookingid):
    connection = getCursor()
    userid = session['member_id']
    connection.execute(
        "SELECT * from specializedclass_booking WHERE specializedclass_bookingid=%s;", (specializedclass_bookingid,))
    booking = connection.fetchone()

    session_id = booking[2]
    connection.execute(
        "Select specializedclasses_id from specializedclass_session WHERE specializedclass_sessionid=%s;", (session_id,))
    class_id = booking[1]
    connection.nextset()
    connection.execute("SELECT sc.pricing FROM specializedclass_session s JOIN specializedclasses sc ON s.specializedclasses_id = sc.specializedclasses_id WHERE s.specializedclass_sessionid=%s;", (class_id,))
    price = connection.fetchone()
    payment_amount = 0
    if price:

        payment_amount = price[0]
    connection.execute("INSERT INTO payment (member_id,payment_date,payment_amount,specializedclass_bookingid) VALUES (%s,%s,%s,%s);",
                       (booking[2], datetime.now(), payment_amount, specializedclass_bookingid))

    return render_template("paymentconfirmation.html", payment_amount=payment_amount)

# Financial report of the gym


@app.route("/financial_report", methods=["GET"])
def financialreport():
    return render_template("financialreport.html")

# monthly report


@app.route("/monthreport", methods=["GET"])
def monthreport():
    connection = getCursor()
    connection.execute(
        "Select * from payment WHERE payment_date >= DATE_SUB(CURDATE(), INTERVAL 1 MONTH);")
    payments = connection.fetchall()
    print(payments)
    total_payment = sum(payment[3] for payment in payments)
    return render_template("monthlyreport.html", payments=payments, total_payment=total_payment)

# six months report


@app.route("/sixmonthreport", methods=["GET"])
def sixmonthreport():
    connection = getCursor()
    connection.execute(
        "Select * from payment WHERE payment_date >= DATE_SUB(CURDATE(), INTERVAL 6 MONTH);")
    payments = connection.fetchall()
    print(payments)
    total_payment = sum(payment[3] for payment in payments)
    return render_template("sixmonthreport.html", payments=payments, total_payment=total_payment)

# annual report


@app.route("/annualreport", methods=["GET"])
def annualreport():
    connection = getCursor()
    connection.execute(
        "Select * from payment WHERE payment_date >= DATE_SUB(CURDATE(), INTERVAL 12 MONTH);")
    payments = connection.fetchall()
    print(payments)
    total_payment = sum(payment[3] for payment in payments)
    return render_template("annualreport.html", payments=payments, total_payment=total_payment)


# member attendance view for admin

@app.route("/admin/attendance", methods=["GET"])
def attendancemember():
    return render_template("memberattendance.html", attendance=[])


@app.route("/admin/attendance", methods=["POST"])
def attendance():
    search = request.form["Search"]
    value = request.form["value"]
    connection = getCursor()

    if search == "firstname":
        searchmember = "%" + value + "%"

        sql = """select at.attendance_id, at.member_id, at.class_date, at.swipe_in, at.swipe_out, at.category, m.firstname, m.mobile
           from attendance at
           JOIN member m ON at.member_id = m.member_id WHERE m.firstname LIKE %s;"""
        connection.execute(sql, (searchmember,))

    elif search == "member_id":
        searchmember = "%" + value + "%"
        sql = """select at.attendance_id, at.member_id, at.class_date, at.swipe_in, at.swipe_out, at.category, m.firstname, m.mobile
           from attendance at
           JOIN member m ON at.member_id = m.member_id WHERE at.member_id LIKE %s;"""
        connection.execute(sql, (searchmember,))

    else:

        sql = """select at.attendance_id, at.member_id, at.class_date, at.swipe_in, at.swipe_out, at.category, m.firstname, m.mobile
           from attendance at
           JOIN member m ON at.member_id = m.member_id WHERE at.member_id LIKE %s OR m.firstname LIKE %s;"""
        connection.execute(sql, (searchmember, searchmember,))

    attendance = connection.fetchall()
    print(attendance)
    return render_template("memberattendance.html", attendance=attendance)

#view the form for contact us
@app.route("/contactus", methods=["GET", "POST"])
def contact():
    if request.method == "POST":
        name = request.form["name"]
        mobile = request.form["mobile"]
        email = request.form["email"]
        message = request.form["message"]
        connection = getCursor()
        connection.execute(
            "Insert into contact(name, mobile, email, message) VALUES (%s,%s,%s,%s);", (name, mobile, email, message,))
        return redirect("/thankyou")
    else:
        return render_template("contactus.html")


@app.route("/thankyou")
def thankyou():
    return render_template("thankyou.html")
