from sqlalchemy.sql.expression import delete
from myapp import myapp_obj

from datetime import date
from myapp.forms import LoginForm, SignupForm, ToDoForm, SearchForm, RenameForm, MdToPdfForm, FlashCards, AddTag

from flask import render_template, request, flash, redirect, make_response, session, url_for
from myapp.models import User, ToDo, load_user, Flashcard, FlashCard, Activity, Cards, Notes
from myapp.render import Render
from myapp import db
import markdown
from sqlalchemy import desc, update, delete, values, func
from flask_login import current_user, login_user, logout_user, login_required
import pdfkit
from werkzeug.utils import secure_filename
import os
import sys
from markdown import markdown
ALLOWED_EXTENSIONS = {'md'}
UPLOAD_FOLDER = 'myapp/upload/'
myapp_obj.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
basedir = 'myapp/text/'


@myapp_obj.route("/")
def welcome():
    """
    This function returns the welcome.html page

    Parameters:
    ----------
        none
    Return:
    ------
        redirect user to welcome page
    """
    return render_template("splashpage.html")


@myapp_obj.route("/loggedin")
@login_required
def log():
    """
    This function returns 'Hi you are logged in' and requires the user to be logged in (@login_required)

    Parameters:
    ----------
        none
    Return:
    ------
        "Hi you are logged in"
    """
    return 'Hi you are logged in'


@myapp_obj.route("/logout/<string:username>")
def logout(username):
    """
    This function logs out the user

    Parameters:
    ----------
        none
    Return:
    ------
        redirects to '/'
    """
    logout_user()
    user = User.query.filter_by(username=username).first()
    data_acitivity = db.session.query(Activity.id, Activity.usertime).group_by(
        Activity.usertime).order_by(desc(Activity.id)).filter(Activity.owner_id == user.id).all()

    for id, dates in data_acitivity:
        id_activity = id
        new_timelogin = dates.timestamp() / 60

    new_timelogout = datetime.datetime.utcnow().timestamp() / 60
    total_time = new_timelogout-new_timelogin

    activity = Activity.query.filter_by(id=id_activity).first()
    activity.timeamount = total_time
    db.session.commit()

    return redirect('/')


@ myapp_obj.route("/login", methods=['GET', 'POST'])
def login():
    """
    This function returns the login page with the LoginForm

    Parameters:
    ----------
        none
    Return:
    ------
        on successful login redirects to 'home.html'
    """
    form = LoginForm()
    if form.validate_on_submit():
        user = User.query.filter_by(username=form.username.data).first()
        if user is None or not user.check_password(form.password.data):
            flash('Incorrect username or password!', 'error')
            return redirect('/login')
        login_user(user, remember=form.remember_me.data)

        exists = db.session.query(Activity.id).filter(
            Activity.owner_id == user.id).order_by(desc(Activity.id)).first() is not None
        if exists:
            user_activity = Activity.query.filter(
                Activity.owner_id == user.id).order_by(desc(Activity.id)).first()
            user_time = user_activity.usertime.strftime("%m-%d-%y")
            today = datetime.datetime.utcnow().strftime("%m-%d-%y")
            if user_time != today:
                time_login = Activity(timeamount=0, owner=user)
                db.session.add(time_login)
                db.session.commit()
        else:
            time_login = Activity(timeamount=0, owner=user)
            db.session.add(time_login)
            db.session.commit()

        return redirect(url_for('home', username=user))
    return render_template('login.html', form=form)


@ myapp_obj.route("/members/<string:name>/")
def getMember(name):
    """
    This function returns the user's name

    Parameters:
    ----------
        none
    Return:
    ------
        Hi + user's name
    """
    return 'Hi ' + name


@ myapp_obj.route("/members/delete")
def deleteMember():
    """
    This function deletes a user from the database

    Parameters:
    ----------
        none
    Return:
    ------
        redirects to login page
    """
    user = current_user.id
    db.session.query(User).filter(
        User.id == user).delete(synchronize_session=False)
    db.session.commit()
    return redirect("/")


@ myapp_obj.route("/signup", methods=['GET', 'POST'])
def signup():
    """
    This function returns the signup page with the SignUpForm

    Parameters:
    ----------
        none
    Return:
    ------
        redirects to login.html
    """
    form = SignupForm()
    if form.validate_on_submit():
        flash(f'Welcome!')
        username = form.username.data
        email = form.email.data
        password = form.password.data
        user = User(username, email)
        user.set_password(form.password.data)
        db.session.add(user)
        db.session.commit()
        return redirect("/login")
    return render_template('signup.html', form=form)


@ myapp_obj.route("/home/<string:username>", methods=['GET', 'POST'])
def home(username):
    """
    This function goes to user's home page

    Parameters:
    ----------
        none
    Return:
    ------
        redirects to user's homepage
    """

    return render_template('home.html', username=username)


@ myapp_obj.route("/todo/<string:username>", methods=['GET', 'POST'])
def todo(username):
    """
    This function returns the ToDo list page with the ToDoForm

    Parameters:
    ----------
        none
    Return:
    ------
        redirect to todo.html
    """
    title = 'To Do List'
    form = ToDoForm()
    if form.validate_on_submit():
        item = form.body.data
        status = form.status.data
        user_id = current_user.id
        todo = ToDo(item, user_id, status)
        db.session.add(todo)
        db.session.commit()
    list = ToDo.query.filter(ToDo.user_id).order_by(ToDo.status.desc())
    return render_template('todo.html', title=title, form=form, list=list, username=username)


@ myapp_obj.route("/todo/inprog/<string:item>", methods=['GET', 'POST'])
def inProgress(item):
    """
    This function changes the todo list item to status: In Progress

    Parameters:
    ----------
        item (string): todo list item's body
    Return:
    ------
        redirect to todo.html
    """
    task = item
    user_id = current_user.id
    username = current_user.username
    update = "In Progress"
    db.session.query(ToDo).filter(
        ToDo.body == task).update({ToDo.status: update})
    db.session.commit()
    return redirect("/todo/<string:username>")


@myapp_obj.route("/todo/update/<string:item>", methods=['GET', 'POST'])
def editTodo(item):
    """
    This function changes the todo list item to status: Todo

    Parameters:
    ----------
        item (string): todo list item's body
    Return:
    ------
        redirect to todo.html
    """
    task = item
    user_id = current_user.id
    username = current_user.username
    update = "Todo"
    db.session.query(ToDo).filter(
        ToDo.body == task).update({ToDo.status: update})
    db.session.commit()
    return redirect("/todo/<string:username>")


@ myapp_obj.route("/todo/comp/<string:item>", methods=['GET', 'POST'])
def complete(item):
    """
    This function changes the todo list item to status: Complete

    Parameters:
    ----------
        item (string): todo list item's body
    Return:
    ------
        redirect to todo.html
    """
    task = item
    user_id = current_user.id
    username = current_user.username
    update = "Complete"
    db.session.query(ToDo).filter(
        ToDo.body == task).update({ToDo.status: update})
    db.session.commit()
    return redirect("/todo/<string:username>")


@ myapp_obj.route("/todo/delete/<string:item>", methods=['GET', 'POST'])
def deleteTodo(item):
    """
    This function deletes a task from the ToDo list

    Parameters:
    ----------
        item (string): todo list item's body
    Return:
    ------
        redirect to todo.html
    """
    task = item
    user_id = current_user.id
    username = current_user.username
    update = "Complete"
    db.session.query(ToDo).filter(ToDo.body == task,
                                  ToDo.user_id == user_id).delete(synchronize_session=False)
    db.session.commit()
    return redirect("/todo/<string:username>")


@ myapp_obj.route("/render/<string:username>")
def renderpage(username):
    """
    This function prints out a list of files that have been uploaded

    Parameters:
    ----------
        none
    Return:
    ------
        return render.html
    """
    basedir = 'myapp/upload/'
    files = os.listdir(basedir)
    return render_template('render.html', files=files, username=username)


@ myapp_obj.route("/render/<string:file>/<string:username>")
def render(file, username):
    """
    Render selected markdown file
    """
    file_path = "myapp/upload/" + file
    html = Render.render(file_path)
    return html


@ myapp_obj.route("/search/<string:username>", methods=['GET', 'POST'])
def search(username):
    """
    This function creates a route for the find-text-in-files feature

        Parameters:
                text: get form the input box
        Returns:
                Show a page for the find-text-in-files feature
    """
    form = SearchForm()
    if form.validate_on_submit():
        result = form.result.data
        results = []
        files = os.listdir(basedir)
        for file in files:
            text = os.path.join(f"{basedir}/{file}")
            with open(text, 'r') as f:
                if result in f.read():
                    results.append(f"{file}")
        return render_template("search.html", form=form, results=results)
    return render_template("search.html", form=form, username=username)


def allowed_file(filename):

    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS


@ myapp_obj.route('/markdown-to-pdf/<string:username>', methods=['GET', 'POST'])
def markdown_to_pdf(username):
    """
    This function creates a route for the markdown-to-pdf feature

            Parameters:
                    file: browse from user's directory
            Returns:
                    Show a page for the markdown-to-pdf feature
    """
    form = MdToPdfForm()
    if request.method == 'POST':
        if 'file' not in request.files:
            flash('No file part')
            return redirect(request.url)
        file = request.files['file']
        if file.filename == '':
            flash('No selected file')
            return redirect(request.url)
        if file and allowed_file(file.filename):
            filename = secure_filename(file.filename)
            file.save(os.path.join(
                myapp_obj.config['UPLOAD_FOLDER'], filename))
            input_file = 'myapp/upload/' + filename

            # add file to db
            body = Render.render(input_file)
            user_id = current_user.id
            aNote = Notes(filename, user_id, body )
            db.session.add(aNote)
            db.session.commit()

            #resume code
            output_file = input_file.split(".md")
            output_file = output_file[0] + '.pdf'
            with open(input_file, 'r') as f:
                html = markdown(f.read(), output_format='html4')
            pdf = pdfkit.from_string(html, False)
            response = make_response(pdf)
            response.headers["Content-Type"] = "application/pdf"
            response.headers["Content-Disposition"] = "inline; filename = output.pdf"
            return response
    return render_template("markdown_to_pdf.html", form=form, username=username)

@ myapp_obj.route('/flashcards-to-pdf/<string:username>', methods=['GET', 'POST'])
def flashcards_to_pdf(username):
    """
    This function creates a route for the flashcards-to-pdf feature
            Returns:
                    Show a page for the flashcards-to-pdf feature
    """
    pdf = pdfkit.from_url(url_for("flashcards",username=username,file="out.pdf"))
    response = make_response(pdf)
    response.headers["Content-Type"] = "application/pdf"
    response.headers["Content-Disposition"] = "inline; filename = output.pdf"
    return response

@ myapp_obj.route('/rename/<string:username>', methods=['GET', 'POST'])
def rename(username):
    """
    This function creates a route for the rename-file feature

            Parameters:
                    file: browse from user's directory
                    new_name: get from input box
            Returns:
                    Show a page for the rename-file feature
    """
    form = RenameForm()
    if request.method == 'POST':
        if 'file' not in request.files:
            flash('No file part')
            return redirect(request.url)
        file = request.files['file']
        if file.filename == '':
            flash('No selected file')
            return redirect(request.url)
        if file and allowed_file(file.filename):
            filename = secure_filename(file.filename)
            file.save(os.path.join(
                myapp_obj.config['UPLOAD_FOLDER'], filename))
            new_name = request.form['new_name']
            os.rename(UPLOAD_FOLDER + filename,
                      UPLOAD_FOLDER + new_name + '.md')
            flash(
                f'Your file was successfully renamed by {form.new_name.data}.md and stored in the path myapp/upload/')
    return render_template("rename.html", form=form, username=username)


"""
@myapp_obj.route("/index/<string:user_name>", methods=["POST", "GET"])
def index(user_name):
    title_homepage = 'Top Page'
    greeting = user_name
    return render_template("index.html", title_pass=title_homepage, XX=greeting)
"""


@myapp_obj.route('/visualizehours/<string:username>', methods=["POST", "GET"])
def visualize(username):
    """
    This class represent for handling visualize hours feature

    Parameters:
    ----------
        username: get from homepage
        activity: filter by username
        flashcard: filter by username
    Return:
    ------
        Perform a page with charts
    """
    title_homepage = 'visualize'
    categories = ['Math', 'Physics', 'English', 'Computer']

    u1 = User.query.filter_by(username=username).first()

    z0 = FlashCard(title='a', defination='0',
                   category=categories[3], owner=u1)
    z1 = FlashCard(title='b', defination='1',
                   category=categories[0], owner=u1)
    z2 = FlashCard(title='c', defination='2',
                   category=categories[2], owner=u1)
    z3 = FlashCard(title='d', defination='3',
                   category=categories[1], owner=u1)
    z3 = FlashCard(title='e', defination='4',
                   category=categories[3], owner=u1)
    db.session.add(z0)
    db.session.add(z1)
    db.session.add(z2)
    db.session.add(z3)
    db.session.commit()

    data_flashcard = db.session.query(db.func.sum(FlashCard.count_category), FlashCard.category).group_by(
        FlashCard.category).order_by(FlashCard.category).filter(FlashCard.owner_id == u1.id).all()

    data_acitivity = db.session.query(Activity.timeamount, Activity.usertime).group_by(
        Activity.usertime).order_by(Activity.usertime).filter(Activity.owner_id == u1.id).all()

    category_labels = []
    count_category_labels = []
    for count_ctr, ctr in data_flashcard:
        category_labels.append(ctr)
        count_category_labels.append(count_ctr)

    amount_labels = []
    date_labels = []
    for amounts, dates in data_acitivity:
        date_labels.append(dates.strftime("%m-%d-%y"))
        amount_labels.append(amounts)

    return render_template("visualizehours.html", title_pass=title_homepage, amounts=amount_labels, dates=date_labels,
                           category=category_labels, c_category=count_category_labels, username=username)


@myapp_obj.route('/trackhours/<string:username>', methods=["POST", "GET"])
def trackinghours(username):
    """
    This class represent for handling tracking hours feature

    Parameters:
    ----------
        username: get from homepage
        flashcard: filter by username
    Return:
    ------
        Perform a page with tables that show their activities
    """
    u1 = User.query.filter_by(username=username).first()
    data_flashcard = db.session.query(FlashCard.id, FlashCard.times_created, FlashCard.title, FlashCard.category).order_by(
        FlashCard.times_created.desc()).filter(FlashCard.owner_id == u1.id).all()

    date_labels = []
    for _, dates, _, _ in data_flashcard:
        temp_date = dates.strftime("%m-%d-%Y")
        if temp_date not in date_labels:
            date_labels.append(temp_date)

    return render_template("trackhours.html", entries=data_flashcard, current_dates=date_labels[0], list_dates=date_labels, username=username)


@myapp_obj.route('/delete-post/<int:entry_id>/<string:username>')
def delete(entry_id, username):
    """
    This class represent for handling delete from table in tracking hour feature

    Parameters:
    ----------
        entry_id: int
    Return:
    ------
        redirect user to tracking hours page
    """
    entry = FlashCard.query.get_or_404(int(entry_id))
    db.session.delete(entry)
    db.session.commit()
    return redirect(url_for("trackinghours", username=username))


@myapp_obj.route("/flashcards/<string:username>", methods=["POST", "GET"])
def flashcards(username):
    title = "Flash Cards"
    user_id = current_user.id
    form = FlashCards()
    if form.validate_on_submit():
        cards = Cards(question=form.question.data, answer=form.answer.data,
                      order=db.session.query(Cards).count(), user_id=user_id)
        db.session.add(cards)
        db.session.commit()
        return redirect(url_for('flashcards', username=username))

    cards = Cards.query.filter(Cards.user_id).order_by(Cards.order.asc()).all()
    return render_template("flashcards.html", title=title, form=form, flash_cards=cards, username=username)


@myapp_obj.route("/question/<num>/<string:username>", methods=["POST", "GET"])
def question(num, username):
    title = "Question " + num
    form = FlashCards()
    checker = ""
    first_card = db.session.query(func.min(Cards.order)).scalar()
    cards = Cards.query.filter(Cards.id == num)
    if Cards.query.filter(Cards.answer == form.answer.data).first():
        checker = "Correct!"
        return render_template("question.html", title=title, form=form, flash_cards=cards, checker=checker, username=username)
    if Cards.query.filter(form.answer.data != None).first():
        checker = "Incorrect"
        order_update = Cards.query.filter_by(
            id=num).update(dict(order=first_card - 1))
        db.session.commit()
    return render_template("question.html", title=title, form=form, flash_cards=cards, checker=checker, username=username)


@myapp_obj.route('/addtags/<string:username>', methods=["POST", "GET"])
def addtags(username):
    form = AddTag()
    if form.validate_on_submit():
        file = form.note.data
        tag = form.tag.data
        user_id = current_user.id
        db.session.query(Notes).filter(
        Notes.name == file).update({Notes.tag: tag})
        db.session.commit()
    files = Notes.query.all()
    return render_template("addtags.html", form=form, files=files, username=username)

@myapp_obj.route('/renderfile/<string:file>/<string:username>', methods=["POST", "GET"])
def renderfile(file, username):
    html = Render.render(file)
    username=username
    return render_template("showfile.html", html=html, username=username)

@myapp_obj.route('/tag/<string:tag>/<string:username>', methods=["GET"])
def tag(tag, username):
    tag = tag
    username = username
    tagfiles = Notes.query.filter(Notes.tag == tag)
    return render_template("taggedfiles.html", tagfiles = tagfiles, tag=tag, username=username)
