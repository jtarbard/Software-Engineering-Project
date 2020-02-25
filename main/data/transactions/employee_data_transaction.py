# Holds all functions related to the employees/managers of the website and the transactions with the database
import logging
import main.data.db_session as db

from main.data.db_classes.employee_data_db_class import Facility, Role, Employee_Router

# Logging has been individually set for this file, as transactions in the database
# are important and must be recorded

logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)

file_handler = logging.FileHandler("logs/transactions.log")
file_handler.setFormatter(logging.Formatter("%(asctime)s:%(name)s:%(message)s"))

logger.addHandler(file_handler)


# Returns all the roles from the composition value passed to the function parameter. EG: 1 = Lifeguard
def return_roles_from_composition_value(binary_rep: int):
    binary_list = [int(x) for x in bin(binary_rep)[2:]] # Retrieves the converted binary list from the composite value
    roles = return_list_of_roles()
    valid_roles = []
    for i in range(len(binary_list)):
        if binary_list[i] == 1: # If the binary value is 1, meaning that the role is valid for that value, then
            try:                # the role is added to the total roles
                valid_roles.append(roles[i])
            except IndexError:
                return False
    return valid_roles # Total roles are returned


# Deduces a composition value that represents the allowed roles for that user
def return_composition_value_from_roles(input_roles: list):
    all_roles = return_list_of_roles().all()
    composite_role = 0
    for current_role in all_roles:
        if current_role.name in [role.lower() for role in input_roles]: # Retrieves ID of role in the database
            composite_role += 2**(current_role.role_id-1)   # Adds binary value to the composite roles
    return composite_role


# Returns list of all roles in the database
def return_list_of_roles():
    session = db.create_session()
    return session.query(Role).all()


# Creates a new role if the conditions are met:
#   - Role name must be between 4 and 20, cannot contain numeric or special characters, and must not already exist
#     in the database
#   - Description must be between 10 and 200
#   - Hourly pay must be between £0 and £50
def create_new_role(role_name: str, description: str, hourly_pay: float):
    if len(role_name) < 4 or len(role_name) > 20 or not role_name.replace(" ", "").isalpha():
        logger.info(f"Failed to add new role {role_name}: role_name not correct length or type")
        return False
    if len(description) < 10 or len(description) > 200:
        logger.info(f"Failed to add new role {role_name}: description not correct length or type")
        return False
    if hourly_pay < 0 or hourly_pay > 50:
        logger.info(f"Failed to add new role {role_name}: invalid discount value")
        return False

    current_roles = return_list_of_roles()
    for role in current_roles:
        if role.role_name == role_name.lower():
            logger.info(f"Failed to add new role {role_name}: role name already exists")
            return False

    new_role = Role()
    new_role.role_name = role_name.lower()
    new_role.description = description
    new_role.hourly_pay = hourly_pay

    session = db.create_session()
    session.add(new_role)
    logger.info(f"Added new role {role_name}")
    session.commit()
    session.close()
    return True


def return_facility_with_id(facility_id: int):
    session = db.create_session()
    return session.query(Facility).filter(Facility.facility_id == facility_id).first()


def return_facility_with_name(facility_name: str):
    session = db.create_session()
    return session.query(Facility).filter(Facility.name == facility_name).first()
