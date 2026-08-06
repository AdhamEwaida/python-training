from course import Course as LegacyCourse
from professor import Professor as LegacyProfessor
from school import Course, GraduateStudent, Professor, Student
from student import Student as LegacyStudent


def test_school_package_exposes_models_from_one_public_interface():
    student = Student("Adham", "S1", [90, 80])
    graduate = GraduateStudent("Lina", "G1", "Flask APIs", [95])
    professor = Professor("Dr. Samir", "P1", "Computer Science")
    course = Course("CS301", "Advanced Python")

    course.add_student(student)
    course.add_student(graduate)
    professor.assign_grade(student, 100)

    assert list(course) == [student, graduate]
    assert student.gpa == 90.0


def test_legacy_modules_reexport_the_packaged_classes():
    assert LegacyCourse is Course
    assert LegacyProfessor is Professor
    assert LegacyStudent is Student
