import sqlalchemy as sa
from sqlalchemy import orm

from main.data.model_base import SqlAlchemyBase


class Employee_Router(SqlAlchemyBase):
    __tablename__ = 'Employee_Router'

    employee_id = sa.Column(sa.Integer, sa.ForeignKey("Employees.employee_id"), nullable=False)
    activity_id = sa.Column(sa.Integer, sa.ForeignKey("Activities.activity_id"), nullable=False)
    role_id = sa.Column(sa.String, sa.ForeignKey("Roles.role_id"), nullable=False)

    __table_args__ = (
        sa.PrimaryKeyConstraint("employee_id","activity_id"),
    )

    activity = orm.relationship("Activity", back_populates="employees", uselist=False)
    role = orm.relationship("Role")


class Facility(SqlAlchemyBase):
    __tablename__ = 'Facilities'

    facility_id = sa.Column(sa.Integer, primary_key=True, autoincrement=True)
    name = sa.Column(sa.String, nullable=False)
    definition = sa.Column(sa.String, nullable=False)
    max_space = sa.Column(sa.Integer, nullable=False)

    activities = orm.relationship("Activity", back_populates="facility")
    activity_types_allowed = orm.relationship("ActivityType", secondary="valid_facility_association", back_populates="allowed_facilities")


class Role(SqlAlchemyBase):
    __tablename__ = 'Roles'

    role_id = sa.Column(sa.Integer, primary_key=True, autoincrement=True)
    role_name = sa.Column(sa.String, nullable=False)
    description = sa.Column(sa.String)
    hourly_pay = sa.Column(sa.Integer, nullable=False)

    employees_with_role = orm.relationship("Employee", secondary="valid_employee_role_association", back_populates="allowed_roles")
    activities_with_role = orm.relationship("ActivityType", secondary="valid_activity_roles_association", back_populates="allowed_roles")


Employee_Role = \
    sa.Table(
        "valid_employee_role_association", SqlAlchemyBase.metadata,
        sa.Column("employee_id", sa.Integer, sa.ForeignKey("Employees.employee_id")),
        sa.Column("role_id", sa.Integer, sa.ForeignKey("Roles.role_id"))
)

Allowed_Facility = \
    sa.Table(
        "valid_facility_association", SqlAlchemyBase.metadata,
        sa.Column("facility_id", sa.Integer, sa.ForeignKey("Facilities.facility_id")),
        sa.Column("activity_type_id", sa.Integer, sa.ForeignKey("ActivityTypes.activity_type_id"))
)

Activity_Roles = \
    sa.Table(
        "valid_activity_roles_association", SqlAlchemyBase.metadata,
        sa.Column("role_id", sa.Integer, sa.ForeignKey("Roles.role_id")),
        sa.Column("activity_type_id", sa.Integer, sa.ForeignKey("ActivityTypes.activity_type_id"))
)
