# Student Portal API

All request and response bodies use JSON. Validation failures return status
`400` with an `error` string and a `details` list. Missing resources return a
resource-specific JSON `404` response.

## Students

| Method | Endpoint | Purpose |
| --- | --- | --- |
| `GET` | `/api/students` | List students; accepts `q`, `page`, and `per_page` |
| `POST` | `/api/students` | Create a student |
| `GET` | `/api/students/<id>` | Read a student |
| `PUT` | `/api/students/<id>` | Replace editable student data |
| `DELETE` | `/api/students/<id>` | Delete a student |

Student writes accept `name`, `email`, `course`, and an optional numeric
`grades` array.

## Courses

| Method | Endpoint | Purpose |
| --- | --- | --- |
| `GET` | `/api/courses` | List courses |
| `POST` | `/api/courses` | Create a course |
| `GET` | `/api/courses/<id>` | Read a course |
| `PUT` | `/api/courses/<id>` | Rename a course |
| `DELETE` | `/api/courses/<id>` | Delete an empty course |

Course writes accept a non-empty `name` of at most 120 characters.

## Users

| Method | Endpoint | Purpose |
| --- | --- | --- |
| `GET` | `/api/users` | List safe user summaries |
| `POST` | `/api/users` | Create an account |
| `GET` | `/api/users/<id>` | Read a safe user summary |
| `PUT` | `/api/users/<id>` | Update username/password |
| `DELETE` | `/api/users/<id>` | Delete an account |

User writes accept `username` and `password`. Passwords are hashed before
storage and are never serialized.

## Enrollments

| Method | Endpoint | Purpose |
| --- | --- | --- |
| `GET` | `/api/students/<id>/enrollments` | List course enrollments |
| `POST` | `/api/students/<id>/enrollments` | Enroll in a course |
| `DELETE` | `/api/students/<id>/enrollments/<course_id>` | Remove enrollment |

Enrollment writes accept an integer `course_id`. Duplicate relationships return
`409 Conflict`.

## HTML upload endpoint

| Method | Endpoint | Purpose |
| --- | --- | --- |
| `POST` | `/students/<id>/profile-picture` | Upload profile image |

Student and course pagination use `page` and `per_page`; search uses `q`.
Collection responses include pagination metadata when query parameters are
provided.
