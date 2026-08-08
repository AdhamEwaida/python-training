"""A small Flask student portal for the practical training exercises."""

from flask import Flask, abort, redirect, render_template, request, url_for
from markupsafe import escape

from student_portal import (
    add_student,
    find_student,
    students,
    validate_student_form,
)

app = Flask(__name__)


@app.route("/", methods=["GET"])
def welcome() -> str:
    """Return the application welcome page."""
    return render_template("index.html")


@app.route("/hello/<name>", methods=["GET"])
def hello(name: str) -> str:
    """Greet the visitor using the name supplied in the URL."""
    return render_template("hello.html", name=escape(name))


@app.route("/students", methods=["GET"])
def student_list() -> str:
    """Render all students currently stored in memory."""
    return render_template("students.html", students=students)


@app.route("/students/<int:student_id>", methods=["GET"])
def student_detail(student_id: int) -> str:
    """Render one student's details and grades."""
    student = find_student(student_id)
    if student is None:
        abort(404)

    average = (
        sum(student["grades"]) / len(student["grades"]) if student["grades"] else None
    )
    return render_template(
        "student_detail.html",
        student=student,
        average=average,
    )


@app.route("/students/register", methods=["GET", "POST"])
def register_student() -> str:
    """Display and process the student registration form."""
    if request.method == "POST":
        form_data, errors = validate_student_form(
            request.form.get("name", ""),
            request.form.get("email", ""),
            request.form.get("course", ""),
            request.form.get("grades", ""),
        )

        if errors:
            return (
                render_template(
                    "register.html",
                    errors=errors,
                    form=request.form,
                ),
                400,
            )

        student = add_student(
            name=str(form_data["name"]),
            email=str(form_data["email"]),
            course=str(form_data["course"]),
            grades=list(form_data["grades"]),
        )
        return redirect(url_for("student_detail", student_id=student["id"]))

    return render_template("register.html", errors=[], form={})


if __name__ == "__main__":
    app.run(debug=True)
