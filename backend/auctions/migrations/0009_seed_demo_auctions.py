from datetime import timedelta
from decimal import Decimal

from django.db import migrations
from django.utils import timezone


DEMO_USERNAME = 'bidzo_demo_seller'
DEMO_EMAIL = 'demo-seller@bidzo.local'


def add_demo_auctions(apps, schema_editor):
    User = apps.get_model('auth', 'User')
    UserProfile = apps.get_model('auctions', 'UserProfile')
    AuctionItem = apps.get_model('auctions', 'AuctionItem')

    seller = User.objects.filter(username=DEMO_USERNAME).first()
    if seller is None:
        seller = User(username=DEMO_USERNAME, email=DEMO_EMAIL, password='!')
        seller.save()
    elif seller.email != DEMO_EMAIL:
        raise RuntimeError(f'Refusing to use existing non-demo account {DEMO_USERNAME!r}.')

    UserProfile.objects.update_or_create(
        user_id=seller.pk,
        defaults={'role': 'seller'},
    )

    samples = [
        {
            'title': 'Sample: Indigo & Gold Beaded Bracelet',
            'description': 'Example listing: a handcrafted bracelet woven with indigo glass beads and gold-tone accents.',
            'category': 'Beaded Jewelry',
            'image_url': 'https://images.unsplash.com/photo-1611652022419-a9419f74343d?auto=format&fit=crop&w=1200&q=85',
            'starting_price': Decimal('450.00'),
            'min_increment': Decimal('50.00'),
            'days_open': 14,
        },
        {
            'title': 'Sample: Sunset Glass Bead Necklace',
            'description': 'Example listing: a colorful artisan necklace inspired by warm sunset shades, made with glass beads.',
            'category': 'Beaded Jewelry',
            'image_url': 'https://images.unsplash.com/photo-1599643478518-a784e5dc4c8f?auto=format&fit=crop&w=1200&q=85',
            'starting_price': Decimal('1200.00'),
            'min_increment': Decimal('100.00'),
            'days_open': 21,
        },
        {
            'title': 'Sample: Beginner Bead Weaving Kit',
            'description': 'Example listing: a starter set with a small loom, assorted beads, thread, and a printed pattern.',
            'category': 'Beading Kits & Supplies',
            'image_url': 'https://images.unsplash.com/photo-1452860606245-08befc0ff44b?auto=format&fit=crop&w=1200&q=85',
            'starting_price': Decimal('800.00'),
            'min_increment': Decimal('50.00'),
            'days_open': 10,
        },
    ]

    now = timezone.now()
    for sample in samples:
        days_open = sample['days_open']
        auction_defaults = {key: value for key, value in sample.items() if key != 'days_open'}
        AuctionItem.objects.get_or_create(
            seller_id=seller.pk,
            title=sample['title'],
            defaults={**auction_defaults, 'end_time': now + timedelta(days=days_open)},
        )


class Migration(migrations.Migration):
    dependencies = [
        ('auctions', '0008_onetimecode_contact_change'),
    ]

    operations = [
        migrations.RunPython(add_demo_auctions, migrations.RunPython.noop),
    ]
