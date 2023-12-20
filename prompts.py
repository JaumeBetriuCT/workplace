TICKET_CLASSIFICATION_PROMPT = """
    Task: You are an employee of a company with the roles {{$role}} and you have to decide if a certain ticket
    that another employee has wrote explaining a problem needs your assistance or not. Respond True if you think
    that your role requires you to solve this ticket or it is for someone else.

    Ticket: {{$input}}
    Note: Do not include any explanations or apologies in your responses. Do not include any text except the
    boolean response.
"""

TICKET_CLASSIFICATION_PROMPT_2 = """
    Task: You have to classify the following ticket in one of the following categories depending on who is the best role to take
    care of the ticket. The categories are:
    - Sales manager
    - Cybersecurity expert
    - IT specialist (printers)
    - IT specialist (office computers)
    - IT specialist (comunication aplications)
    - Frontend engineer
    - Data expert

    Ticket: {{$input}}
    Note: Your response should only contain the category. Avoid including any explanations, apologies, or additional text.
"""