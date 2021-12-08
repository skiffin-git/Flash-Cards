from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, BooleanField, SubmitField, SelectField
from wtforms.validators import (DataRequired, Email, EqualTo, Length)
from flask_wtf.file import FileField, FileRequired

class LoginForm(FlaskForm):
        """
    This class creates a user login form

            Parameters:
                    username (StringField): A single line of text for user to input name
                    password (PasswordField): A single line of text for users to enter password
                    remember_me (BooleanField): a checkbox
                    submit (SubmitField)

            Returns:
                    Show a login form
    """
        __tablename__ = 'users'
        username = StringField('Username', validators=[DataRequired()])
        password = PasswordField('Password', validators=[DataRequired()])
        remember_me = BooleanField('Remember me', default=False)
        submit = SubmitField('Log In')

class SignupForm(FlaskForm):
        """
         This class creates a user signup form

            Parameters:
                    username (StringField): A single line of text for user to input name
                    email (StringField): A single line of text for users to input email
                    password (PasswordField): A single line of text for users to enter password
                    confirm (PasswordFeild): A single line of text for users to re-enter password
                    submit (SubmitField)

            Returns:
                    Show a signup form
        """
        username = StringField('Username', validators=[DataRequired()])
        email = StringField('Email', validators=[DataRequired()])
        password = PasswordField('Password', validators=[DataRequired(), Length(min=6, message='Select a stronger password.')])
        confirm = PasswordField('Confirm yor password', validators=[DataRequired(), EqualTo('password', message='Passwords must match.')])
        submit = SubmitField('Register')

class ToDoForm(FlaskForm):
        """
        This class creates a todo list item form

            Parameters:
                    body (StringField): A single line text field for user to enter todo item
                    status (SelectField): A list of Status' to choose from
                    submit (SubmitField): Submit button

            Returns:
                    Show a todo list form
        """
        body = StringField('To Do Item', validators=[DataRequired()])
        status = SelectField('Status', choices = ['Todo', 'In Progress', 'Complete'])
        submit = SubmitField('Submit')

class SearchForm(FlaskForm):
        """
	This class creates a search form for the find-text-in-files feature

            Parameters:
                    result (StringField): A single line of text
                    sumbit (SubmitField): A submit button
            Returns:
                    Show a search form for the find-text-in-files feature
	"""
        result = StringField('Result', validators=[DataRequired()])
        submit = SubmitField('Search')

class RenameForm(FlaskForm):
        """
	This class creates a rename form for the rename-file feature

            Parameters:
                    file (FileField): A file
		    new_name(StringField): A single line of text
                    sumbit (SubmitField): A submit button
            Returns:
                    Show a rename form for the rename-file feature
	"""
        file = FileField('File', validators=[FileRequired()])
        new_name = StringField('New name', validators=[DataRequired()])
        submit = SubmitField('Rename')

class MdToPdfForm(FlaskForm):
        """
	This class creates a markdown-to-pdf form for the markdown-to-pdf feature

            Parameters:
                    file (FileField): A file
                    sumbit (SubmitField): A submit button
            Returns:
                    Show a markdown-to-pdf form for the markdown-to-pdf feature
	"""
        file = FileField('File', validators=[FileRequired()])
        submit = SubmitField('Convert')

class FlashCards(FlaskForm):
        question = StringField()
        answer = StringField(validators=[DataRequired()])
        submit = SubmitField("Submit")

class AddTag(FlaskForm):
        """
	This class adds a tag to notes

            Parameters:
                    tag (StringField): A tag
                    sumbit (SubmitField): A submit button
            Returns:
                    Show a markdown-to-pdf form for the markdown-to-pdf feature
	"""
        note = StringField ('Which Notes would you like to add a tag to?')
        tag = StringField("Add a Tag")
        submit = SubmitField("Submit")
