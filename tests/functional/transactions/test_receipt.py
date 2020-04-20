

"""
<Rule '/transactions/view_individual_receipts/<receipt_id>' (OPTIONS, HEAD, GET) -> transactions.e_m_get>
<Rule '/transactions/receipts/<encrypted_receipt>' (OPTIONS, HEAD, GET) -> transactions.receipt_get>
<Rule '/transactions/receipts/check_receipt_input' (OPTIONS, POST) -> transactions.check_receipt_qr_code>
"""