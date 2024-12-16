from django.core.management.base import BaseCommand
from django.core.management import call_command

class Command(BaseCommand):
    help = 'Add users, measurements, and invoices to the database'

    def handle(self, *args, **kwargs):
        try:
            # Step 1: Add users
            self.stdout.write(self.style.SUCCESS("Executing: Add Users"))
            call_command('add_users')  # Replace 'add_users' with the actual command name to add users
            self.stdout.write(self.style.SUCCESS("Users added successfully."))
            
            # Step 2: Add measurements and invoices
            self.stdout.write(self.style.SUCCESS("Executing: Add Measurements and Invoices"))
            call_command('add_measurements_and_invoices')  # Replace with the actual command name
            self.stdout.write(self.style.SUCCESS("Measurements and invoices added successfully."))
        
        except Exception as e:
            self.stdout.write(self.style.ERROR(f"An error occurred: {str(e)}"))
