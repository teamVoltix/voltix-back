from django.core.management.base import BaseCommand
from apps.general.models import User  # Replace 'myapp' with the name of your Django app

class Command(BaseCommand):
    help = 'Add users to the custom User table'

    def handle(self, *args, **kwargs):
        # List of users to add
        users = [
            {"dni": "X7283947H", "fullname": "Mariana Lopes", "email": "mariana.lopes@yahoo.com"},
            {"dni": "12345678S", "fullname": "Giovanni Russo", "email": "giovanni.russo@gmail.com"},
            {"dni": "B4567832L", "fullname": "Sofia Kovalenko", "email": "sofia.kovalenko@outlook.com"},
            {"dni": "Y3456789V", "fullname": "Miguel Fernández", "email": "miguel.fernandez@mail.com"},
            {"dni": "23456789P", "fullname": "Anna Müller", "email": "anna.muller@protonmail.com"},
            {"dni": "C7834591R", "fullname": "Ravi Patel", "email": "ravi.patel@hotmail.com"},
            {"dni": "A2345671T", "fullname": "Amina Ben Said", "email": "amina.bensaid@icloud.com"},
            {"dni": "98765432Y", "fullname": "Oliver Smith", "email": "oliver.smith@gmail.com"},
            {"dni": "K2837465X", "fullname": "Francesco De Luca", "email": "francesco.deluca@yahoo.com"},
            {"dni": "67891234N", "fullname": "Yasmin Khalil", "email": "yasmin.khalil@163.com"}
        ]

        for user_data in users:
            if not User.objects.filter(dni=user_data["dni"]).exists():
                user = User.objects.create_user(
                    dni=user_data["dni"],
                    fullname=user_data["fullname"],
                    email=user_data["email"],
                    password="1234Aa@"
                )
                self.stdout.write(self.style.SUCCESS(f"User '{user.fullname}' created successfully!"))
            else:
                self.stdout.write(f"User with DNI '{user_data['dni']}' already exists.")
