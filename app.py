"""A small Flask student portal for the practical training exercises."""

from flask import Flask, redirect, render_template, request, url_for
from markupsafe import escape

app = Flask(__name__)

students: list[dict[str, str]] = []


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


@app.route("/students/register", methods=["GET", "POST"])
def register_student() -> str:
    """Display and process the student registration form."""
    if request.method == "POST":
        name = request.form.get("name", "").strip()
        email = request.form.get("email", "").strip()
        course = request.form.get("course", "").strip()

        errors = []
        if not name:
            errors.append("Name is required.")
        if not email or "@" not in email:
            errors.append("A valid email is required.")
        if not course:
            errors.append("Course is required.")

        if errors:
            return (
                render_template(
                    "register.html",
                    errors=errors,
                    form=request.form,
                ),
                400,
            )

        students.append({"name": name, "email": email, "course": course})
        return redirect(url_for("student_list"))

    return render_template("register.html", errors=[], form={})


if __name__ == "__main__":
    app.run(debug=True)
