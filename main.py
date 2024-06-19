from flask import Flask, render_template, redirect, url_for
from flask_bootstrap import Bootstrap5
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column
from sqlalchemy import Integer, String, Boolean, DateTime
from flask_wtf import FlaskForm
from wtforms import StringField, SelectField, DateTimeField, SubmitField, IntegerField
from wtforms.validators import DataRequired, Optional
from wtforms.widgets import html_params
import datetime


class DateTimeLocalInput(object):
    input_type = 'datetime-local'

    def __call__(self, field, **kwargs):
        kwargs.setdefault('id', field.id)
        if 'value' not in kwargs:
            kwargs['value'] = field._value()
        return f'<input type="{self.input_type}" {html_params(name=field.name, **kwargs)}>'


class AddTodo(FlaskForm):
    what = StringField("What do we need", validators=[DataRequired()])
    where = StringField("Where do we want it from")
    how_much = IntegerField("How much do we need")
    units = SelectField("What units",
                        choices=[
                            ("", "-"),
                            ("kg", "kg"),
                            ("l", "l"),
                            ("pkgs", "pkgs")
                        ])
    until = DateTimeField('Until', format='%Y-%m-%dT%H:%M', validators=[Optional()], widget=DateTimeLocalInput())
    submit = SubmitField("Submit Cafe")


app = Flask(__name__)
app.config['SECRET_KEY'] = 'yoursecretkey'
Bootstrap5(app)


class Base(DeclarativeBase):
    pass


app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///todo.db'
db = SQLAlchemy(model_class=Base)
db.init_app(app)


class Todo(db.Model):
    __tablename__ = "todo"
    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    what: Mapped[str] = mapped_column(String(250), nullable=False)
    where: Mapped[str] = mapped_column(String(250), nullable=True)
    how_much: Mapped[int] = mapped_column(Integer, nullable=True)
    units: Mapped[str] = mapped_column(String(25), nullable=True)
    until: Mapped[datetime.datetime] = mapped_column(DateTime, nullable=True)
    done: Mapped[bool] = mapped_column(Boolean, default=False)
    created_at = db.Column(db.DateTime, default=datetime.datetime.utcnow)


with app.app_context():
    db.create_all()


@app.route('/')
def todo():
    todos = Todo.query.filter_by(done=False).all()
    completed_todos = Todo.query.filter_by(done=True).all()
    return render_template("index.html", todos=todos, completed_todos=completed_todos)


@app.route('/add', methods=["GET", "POST"])
def add_todo():
    form = AddTodo()
    if form.validate_on_submit():
        new_todo = Todo(
            what=form.what.data,
            where=form.where.data,
            how_much=form.how_much.data,
            units=form.units.data,
            until=form.until.data
        )
        db.session.add(new_todo)
        db.session.commit()
        return redirect(url_for("todo"))
    return render_template("add_todo.html", form=form)

@app.route('/mark_as_done/<int:todo_id>', methods=['POST'])
def mark_as_done(todo_id):
    marked_todo = Todo.query.get_or_404(todo_id)
    marked_todo.done = True
    db.session.commit()
    return redirect(url_for('todo'))

@app.route('/remove_todo/<int:todo_id>', methods=['POST'])
def remove_todo(todo_id):
    removed_todo = Todo.query.get_or_404(todo_id)
    db.session.delete(removed_todo)
    db.session.commit()
    return redirect(url_for('todo'))

if __name__ == "__main__":
    app.run(debug=True, port=5002)

