from main.data.db_session import database


class Employee_Router(database.Model):
    __tablename__ = 'Employee_Router'

    employee_id = database.Column(database.Integer, database.ForeignKey("Employees.employee_id"), nullable=False)
    activity_id = database.Column(database.Integer, database.ForeignKey("Activities.activity_id"), nullable=False)
    role_id = database.Column(database.String, database.ForeignKey("Roles.role_id"), nullable=False)

    __table_args__ = (
        database.PrimaryKeyConstraint("employee_id","activity_id"),
    )

    activity = database.relationship("Activity", back_populates="employees", uselist=False)
    role = database.relationship("Role")


class Facility(database.Model):
    __tablename__ = 'Facilities'

    facility_id = database.Column(database.Integer, primary_key=True, autoincrement=True)
    name = database.Column(database.String, nullable=False)
    definition = database.Column(database.String, nullable=False)
    max_space = database.Column(database.Integer, nullable=False)

    activities = database.relationship("Activity", back_populates="facility")


class Role(database.Model):
    __tablename__ = 'Roles'

    role_id = database.Column(database.Integer, primary_key=True, autoincrement=True)
    role_name = database.Column(database.String, nullable=False)
    description = database.Column(database.String)
    hourly_pay = database.Column(database.Integer, nullable=False)
