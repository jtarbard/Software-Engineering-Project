import sqlalchemy as sa
from main.data.model_base import SqlAlchemyBase


class Employee_Router(SqlAlchemyBase):
    __tablename__ = 'Employee_Router'

    Employee_id = sa.Column(sa.Integer, sa.ForeignKey("Employees.employee_id"), nullable=False)
    Activity_id = sa.Column(sa.Integer, sa.ForeignKey("Activities.activity_id"), nullable=False)
    Role = sa.Column(sa.String, sa.ForeignKey("Roles.role_id"), nullable=False)

    __table_args__ = (
        sa.PrimaryKeyConstraint("Employee_id","Activity_id"),
    )


class Facility(SqlAlchemyBase):
    __tablename__ = 'Facilities'

    facility_id = sa.Column(sa.Integer, primary_key=True, autoincrement=True)
    name = sa.Column(sa.String, nullable=False)
    definition = sa.Column(sa.String, nullable=False)
    max_space = sa.Column(sa.Integer, nullable=False)


class Role(SqlAlchemyBase):
    __tablename__ = 'Roles'

    role_id = sa.Column(sa.Integer, primary_key=True, autoincrement=True)
    role_name = sa.Column(sa.String, nullable=False)
    description = sa.Column(sa.String)
    hourly_pay = sa.Column(sa.Integer, nullable=False)
