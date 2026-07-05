from django.core.management.base import BaseCommand
from expapp.models import Category

class Command(BaseCommand):
    help = 'Populate default expense categories'

    def handle(self, *args, **options):
        categories = [
            {'name': 'Food & Dining', 'icon': '🍽️', 'color': '#ff6b6b'},
            {'name': 'Travel', 'icon': '✈️', 'color': '#4ecdc4'},
            {'name': 'Shopping', 'icon': '🛍️', 'color': '#45b7d1'},
            {'name': 'Rent & Utilities', 'icon': '🏠', 'color': '#96ceb4'},
            {'name': 'Bills & Payments', 'icon': '💳', 'color': '#feca57'},
            {'name': 'Health & Medical', 'icon': '🏥', 'color': '#ff9ff3'},
            {'name': 'Entertainment', 'icon': '🎬', 'color': '#54a0ff'},
            {'name': 'Education', 'icon': '📚', 'color': '#5f27cd'},
            {'name': 'Transportation', 'icon': '🚗', 'color': '#00d2d3'},
            {'name': 'Others', 'icon': '📦', 'color': '#7c3aed'},
        ]

        for cat_data in categories:
            category, created = Category.objects.get_or_create(
                name=cat_data['name'],
                defaults={
                    'icon': cat_data['icon'],
                    'color': cat_data['color']
                }
            )
            if created:
                self.stdout.write(
                    self.style.SUCCESS(f'Created category: {category.name}')
                )
            else:
                self.stdout.write(
                    self.style.WARNING(f'Category already exists: {category.name}')
                )

        self.stdout.write(
            self.style.SUCCESS('Successfully populated expense categories!')
        )