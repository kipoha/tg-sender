import random

from django.core.management.base import BaseCommand
from django.core.management import call_command

from unittest.mock import patch

class Command(BaseCommand):
    help = 'Automatically create migrations'

    def handle(self, *args, **options):
        
        def mock_input():
            return random.choice(["1", "y"])

        with patch('builtins.input', mock_input):
            self.stdout.write("Migrating...\n")
            call_command('makemigrations', *args, **options)
