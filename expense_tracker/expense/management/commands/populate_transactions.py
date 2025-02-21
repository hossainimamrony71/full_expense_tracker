from django.core.management.base import BaseCommand
from django.contrib.auth import get_user_model
from account.models import User
from expense.models import ExpenseCategory, ExpenseSubCategory, Transaction
from django.utils import timezone
import random
import decimal
from datetime import datetime, timedelta
import pytz

class Command(BaseCommand):
    help = 'Populate the Transaction model with sample data within a date range'

    def add_arguments(self, parser):
        # Optional arguments for start and end dates
        parser.add_argument(
            '--start_date',
            type=str,
            help='Specify the start date in YYYY-MM-DD format'
        )
        parser.add_argument(
            '--end_date',
            type=str,
            help='Specify the end date in YYYY-MM-DD format'
        )

    def handle(self, *args, **options):
        # Fetch the user (replace 'admin' with the actual username or adjust accordingly)
        User = get_user_model()
        try:
            user = User.objects.get(username='admin')
        except User.DoesNotExist:
            self.stdout.write(self.style.ERROR('User "admin" does not exist. Please create this user or adjust the username.'))
            return

        # Fetch all categories
        categories = ExpenseCategory.objects.all()

        if not categories.exists():
            self.stdout.write(self.style.ERROR('No ExpenseCategory instances found. Please populate ExpenseCategory first.'))
            return

        # Sample sources
        sources = ['cash', 'bank transfer', 'credit card', 'mobile payment']

        # Get start and end dates from command arguments or set defaults
        start_date_str = options.get('start_date')
        end_date_str = options.get('end_date')

        # Set timezone
        tz = pytz.timezone('UTC')  # Adjust to your timezone if necessary

        if start_date_str:
            start_date = datetime.strptime(start_date_str, '%Y-%m-%d')
            start_date = tz.localize(start_date)
        else:
            # Default to 30 days ago
            start_date = timezone.now() - timedelta(days=30)
            start_date = start_date.replace(hour=0, minute=0, second=0, microsecond=0)

        if end_date_str:
            end_date = datetime.strptime(end_date_str, '%Y-%m-%d')
            end_date = tz.localize(end_date)
        else:
            # Default to today
            end_date = timezone.now()
            end_date = end_date.replace(hour=23, minute=59, second=59, microsecond=999999)

        # Ensure start_date is before end_date
        if start_date > end_date:
            self.stdout.write(self.style.ERROR('Start date must be before or equal to end date.'))
            return

        # Calculate the total number of days between start and end dates
        total_days = (end_date.date() - start_date.date()).days + 1  # Inclusive of end date

        total_transactions_created = 0

        for day_offset in range(total_days):
            current_date = start_date + timedelta(days=day_offset)
            transactions_count = random.randint(8, 15)
            transactions_created = 0

            for _ in range(transactions_count):
                # Select a random category
                category = random.choice(categories)

                # Fetch subcategories under the selected category
                subcategories = ExpenseSubCategory.objects.filter(parent=category)
                if subcategories.exists():
                    subcategory = random.choice(subcategories)
                else:
                    # If no subcategories exist, create one
                    subcategory_name = f"Subcategory {random.randint(1, 10000)}"
                    subcategory = ExpenseSubCategory.objects.create(
                        parent=category,
                        name=subcategory_name,
                        created_by=user
                    )

                # Generate random amount
                amount_value = decimal.Decimal(random.uniform(50.0, 10000.0)).quantize(decimal.Decimal('0.01'))

                # Select a random source
                source = random.choice(sources)

                # Generate a unique voucher
                voucher = f"VOUCHER-{timezone.now().strftime('%Y%m%d%H%M%S%f')}-{random.randint(1, 100000)}"

                # Generate a random time on the current date
                random_hour = random.randint(0, 23)
                random_minute = random.randint(0, 59)
                random_second = random.randint(0, 59)
                created_at = current_date.replace(hour=random_hour, minute=random_minute, second=random_second)

                # Create the transaction
                transaction = Transaction.objects.create(
                    user=user,
                    ammount=amount_value,
                    category=category,
                    subcategory=subcategory,
                    source=source,
                    voucher=voucher,
                    created_at=created_at
                )

                transactions_created += 1
                total_transactions_created += 1

            self.stdout.write(self.style.SUCCESS(
                f"Created {transactions_created} transactions for {current_date.strftime('%Y-%m-%d')}"))

        self.stdout.write(self.style.SUCCESS(
            f"Successfully created a total of {total_transactions_created} transactions from {start_date.strftime('%Y-%m-%d')} to {end_date.strftime('%Y-%m-%d')}."))
