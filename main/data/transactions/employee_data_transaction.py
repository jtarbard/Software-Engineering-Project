# Holds all functions related to the employees/managers of the website and the transactions with the database
from main.data.db_session import add_to_database
from main.data.db_classes.employee_data_db_class import Role, Employee_Router
from main.data.db_classes.activity_db_class import Facility, ActivityType
from main.logger import log_transaction

# Returns list of all roles in the database
def return_list_of_roles():
    return Role.query(Role).all()


# Creates a new role if the conditions are met:
#   - Role name must be between 4 and 20, cannot contain numeric or special characters, and must not already exist
#     in the database
#   - Description must be between 10 and 200
#   - Hourly pay must be between £0 and £50
#   [Lewis.s]
def create_new_role(role_name: str, description: str, hourly_pay: float):
    if len(role_name) < 4 or len(role_name) > 20 or not role_name.replace(" ", "").isalpha():
        log_transaction(f"Failed to add new role {role_name}: role_name not correct length or type")
        return False
    if len(description) < 10 or len(description) > 200:
        log_transaction(f"Failed to add new role {role_name}: description not correct length or type")
        return False
    if hourly_pay < 0 or hourly_pay > 50:
        log_transaction(f"Failed to add new role {role_name}: invalid discount value")
        return False

    current_roles = return_list_of_roles()
    for role in current_roles:
        if role.role_name == role_name.lower():
            log_transaction(f"Failed to add new role {role_name}: role name already exists")
            return False

    new_role = Role()
    new_role.role_name = role_name.lower()
    new_role.description = description
    new_role.hourly_pay = hourly_pay

    add_to_database(new_role)
    log_transaction(f"Added new role {role_name}")
    return True


def return_facility_with_id(facility_id: int):
    return Facility.query.filter(Facility.facility_id == facility_id).first()


def return_facility_with_name(facility_name: str):
    return Facility.query.filter(Facility.name == facility_name).first()


def return_facility_name_with_facility_id(facility_id):
    facility = Facility.query(Facility).filter(Facility.facility_id == facility_id).first()
    return facility.name


def return_role_id_with_name(role):
    role = Role.query(Role).filter(Role.role_name == role).first()
    if not role:
        log_transaction(f"Failed to return role {role}")
    return role


def add_role_to_activity_type(role_id, activity_type_id):
    role = Role.query(Role).filter(Role.role_id == role_id).first()
    activity_type = ActivityType.query(ActivityType).filter(ActivityType.activity_type_id == activity_type_id).first()

    role.activities_with_role.append(activity_type)
