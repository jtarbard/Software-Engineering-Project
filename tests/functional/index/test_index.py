

def test_index_func(generic_route_test, index_func_data):
    index_func_data["test_route"] = "/"
    index_func_data["database_tables"] = ["facility", "activity_type", "activity", "membership_type",
                                          "customer", "customer_with_membership", "membership_receipt",
                                          "membership"]

    generic_route_test(request_type="GET",
                       data=index_func_data)

    # --------------------------------- END OF THIS TEST: test_index_func --------------------------------- #
