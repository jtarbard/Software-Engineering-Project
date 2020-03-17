from main.data.db_classes.transaction_db_class import Receipt
from main.data.db_classes.user_db_class import User
from flask_mail import Message
import qrcode


def return_email_message(receipt: Receipt, new_user: User):
    message = Message(f"Vertex Booking Receipt", recipients=[f"{new_user.email}"])
    message.html = """"<h1>Thank you for purchasing at The Vertex</h1> <br>
                               <h3>Receipt:</h3>
                               <table> 
                                    <thead>
                                        <tr><td colspan="4"><h6> Classes brought &nbsp</h6></td></tr>
                                    </head>
                                    <tbody> 
                                        <tr> 
                                            <td><strong>Class Name &nbsp</strong></td>
                                            <td><strong>Class Start Time &nbsp</strong></td>
                                            <td><strong>Class End Time &nbsp</strong></td>
                                            <td><strong>Facility &nbsp</strong></td>
                                        </tr>
                                        <tr>
                                        """
    for booking in receipt.bookings:
        message.html += f"""
                    <tr>
                        <td>{booking.activity.activity_type.name}</td>
                        <td>{booking.activity.start_time}</td>
                        <td>{booking.activity.end_time}</td>
                        <td>{booking.activity.facility.name}</td>
                    <tr>
                    """

    if receipt.membership:
        message.html += f"""
                    <tr>
                        <td colspan="4" rowspan="1"></td>
                    </tr>
                    <tr>
                        <td colspan="4"><h6>Membership</h6></td>
                    </tr>
                    <tr> 
                        <td><strong>Membership Name &nbsp</strong></td>
                        <td><strong>Start Time &nbsp</strong></td>
                        <td><strong>End Time &nbsp</strong></td>
                        <td><strong>Discount &nbsp</strong></td>
                    </tr>
                    <tr> 
                        <td>{receipt.membership.membership_type.name} &nbsp</td>
                        <td>{receipt.membership.start_date} &nbsp</td>
                        <td>{receipt.membership.start_date} &nbsp</td>
                        <td>{receipt.membership.membership_type.discount} &nbsp</td>
                    </tr>
                """
    message.html += f"""
                    <tr>
                        <td colspan="2"></td>
                        <td><strong>Total Price: &nbsp</strong></td>
                        <td>{receipt.total_cost}</td>
                    </tr>
                </tbody>
            </table>
            """
    return message


def create_new_qrcode_image(file_direct, encrypted_receipt):
    qr = qrcode.QRCode(
        version=1,
        error_correction=qrcode.constants.ERROR_CORRECT_L,
        box_size=10,
        border=4,
    )
    qr.add_data(encrypted_receipt)
    qr.make(fit=True)

    img = qr.make_image(fill_color="black", back_color="white")
    img.save(file_direct)