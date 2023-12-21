from django.contrib.auth import get_user_model
from django.core.management.base import BaseCommand
from django.utils import timezone

from word_bank.models import UserWord, WordInfo


class Command(BaseCommand):
    help = "Generate a usage report"
    
    def handle(self, *args, **options):
        time = timezone.now().strftime("%Y-%m-%d %H:%M:%S")
        self.stdout.write("Usage report generated at", ending=" ")
        self.stdout.write(self.style.MIGRATE_HEADING(time))
        
        num_word_infos = WordInfo.objects.count()
        self.stdout.write("Total number of word infos:", ending=" ")
        self.stdout.write(self.style.SUCCESS(str(num_word_infos)))

        num_users = get_user_model().objects.count()
        self.stdout.write("Total number of users:", ending=" ")
        self.stdout.write(self.style.SUCCESS(f"{num_users:>7}"))
        
        num_user_words = UserWord.objects.count()
        self.stdout.write("Total number of user words:", ending=" ")
        self.stdout.write(self.style.SUCCESS(str(num_user_words)))
        