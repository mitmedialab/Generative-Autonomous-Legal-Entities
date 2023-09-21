import re


def parse_latest_reply(email_body):
    pattern = r"^(.*?)On (.*?) wrote:(.*?)$"

    # Search for the pattern in the email body
    match = re.search(pattern, email_body, re.DOTALL | re.IGNORECASE | re.MULTILINE)

    return match.group(1).strip() if match else email_body


email_body = """
Thanks Joe,\r\nTell me more about specific services and prices.\r\n\r\nOn Thu, Sep 14, 2023 at 12:38\xe2\x80\xafPM <llmentity@gmail.com> wrote:\r\n\r\n> Hi Roman,\r\n>\r\n> Absolutely! At Matcha Digital Widgets, we provide premium digital\r\n> widget solutions to clients in the Technology & Innovation, Energy &\r\n> Infrastructure, and Finance sectors globally. Our teams excel in\r\n> seamless transactional execution, winning paths strategies, and\r\n> forward-looking market solutions. We specialize in helping innovators\r\n> navigate the convergence of technology with finance, energy, and life\r\n> sciences. How can we assist you in achieving better business outcomes?\r\n>\r\n> Best regards,\r\n> Joe Pavelski\r\n>\r\n
"""

parse_latest_reply(email_body)
