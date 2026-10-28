from django.core.management.base import BaseCommand
from catering.models import Dish, Testimonial

CON = [("Grilled herb chicken", "With garlic mash and buttered vegetables", True),
       ("Beef lasagna", "Layered pasta, rich tomato and béchamel", False),
       ("Chicken alfredo", "Creamy parmesan pasta with grilled chicken", False),
       ("Lemon butter salmon", "Oven-roasted fillet, asparagus, baby potatoes", False),
       ("Peppered steak", "Seared beef in black pepper sauce", False),
       ("Finger food platters", "Club sandwiches, mini quiches, spring rolls", False)]
INT = [("Butter chicken and naan", "Mild tomato-cream curry, fresh flatbread", True),
       ("Chinese fried rice", "With sweet and sour chicken or crispy beef", False),
       ("Thai green curry", "Coconut curry with vegetables and jasmine rice", False),
       ("Shawarma platters", "Chicken or beef wraps with garlic sauce", False),
       ("Moroccan lamb tagine", "Slow-cooked lamb, apricots, couscous", False),
       ("Greek gyros", "Pita, grilled meat, tzatziki, salad", False)]
QUOTES = [("Every guest asked who the caterer was. The lasagna disappeared first.", "Sample review: wedding client"),
          ("Hot food, on time, for 120 staff. We booked again for December.", "Sample review: corporate client"),
          ("The butter chicken and the grilled salmon on one table? Perfect.", "Sample review: birthday client")]


class Command(BaseCommand):
    help = "Load the starter menu and sample reviews (safe to re-run)."

    def handle(self, *args, **opts):
        for cuisine, items in ((Dish.CONTINENTAL, CON), (Dish.INTERCONTINENTAL, INT)):
            for i, (n, d, p) in enumerate(items):
                Dish.objects.get_or_create(name=n, cuisine=cuisine,
                                           defaults={"description": d, "is_popular": p, "position": i})
        for q, a in QUOTES:
            Testimonial.objects.get_or_create(quote=q, defaults={"author": a})
        self.stdout.write(self.style.SUCCESS("Menu and reviews loaded."))
