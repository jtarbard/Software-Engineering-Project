from main.data.db_classes.activity_db_class import activity_roles
from main.data.db_session import database

# intermediate table that enables many-to-many relationship between ActivityType and Facility
employee_role = \
    database.Table("valid_employee_role_association",
        database.Column("employee_id", database.Integer, database.ForeignKey("Employees.employee_id")),
        database.Column("role_id", database.Integer, database.ForeignKey("Roles.role_id"))
)


class Employee_Router(database.Model):
    __tablename__ = 'Employee_Router'

    employee_id = database.Column(database.Integer, database.ForeignKey("Employees.employee_id"), nullable=False)
    activity_id = database.Column(database.Integer, database.ForeignKey("Activities.activity_id"), nullable=False)
    role_id = database.Column(database.Integer, database.ForeignKey("Roles.role_id"), nullable=False)

    __table_args__ = (
        database.PrimaryKeyConstraint("employee_id", "activity_id"),
    )

    activity = database.relationship("Activity", back_populates="employees", uselist=False)
    role = database.relationship("Role")


class Role(database.Model):
    __tablename__ = 'Roles'

    role_id = database.Column(database.Integer, primary_key=True, autoincrement=True)
    role_name = database.Column(database.String, nullable=False)
    description = database.Column(database.String)
    hourly_pay = database.Column(database.Integer, nullable=False)

    employees_with_role = database.relationship("Employee",
                                                secondary=employee_role,
                                                backref=database.backref("allowed_roles", lazy="dynamic"))

    activities_with_role = database.relationship("SessionType",
                                                 secondary=activity_roles,
                                                 backref=database.backref("allowed_roles", lazy="dynamic"))

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.role_name = kwargs.get("role_name", "UNSET_ROLE").lower()
