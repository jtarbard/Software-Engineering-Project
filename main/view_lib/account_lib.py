import main.data.transactions.user_db_transaction as udf
from main.data.db_classes.user_db_class import Customer


def get_membership_type(user):
    membership = None
    if user.__mapper_args__['polymorphic_identity'] == "Customer":
        customer: Customer = udf.return_customer_with_user_id(user.user_id)

        if customer.current_membership is not None:
            membership = customer.current_membership.membership_type

    return membership