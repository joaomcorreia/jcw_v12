from datetime import timedelta

from django.core.management.base import BaseCommand
from django.utils import timezone

from core.models import BlogCategory, BlogPost


def build_translations(en_text, nl_text):
    return {
        "en": en_text,
        "nl": nl_text,
        "fr": "Translation coming soon",
        "de": "Translation coming soon",
        "es": "Translation coming soon",
        "pt": "Translation coming soon",
    }


class Command(BaseCommand):
    help = "Seed initial blog categories and posts."

    def handle(self, *args, **options):
        categories = [
            ("website-tips", build_translations("Website Tips", "Website tips")),
            ("visibility-seo", build_translations("Visibility & SEO", "Zichtbaarheid en SEO")),
            ("printlab", build_translations("PrintLab", "PrintLab")),
            ("updates", build_translations("Updates", "Updates")),
        ]

        category_map = {}
        for slug, name in categories:
            category, _ = BlogCategory.objects.get_or_create(
                slug=slug,
                defaults={"name": name, "is_active": True},
            )
            if category.name != name:
                category.name = name
                category.is_active = True
                category.save(update_fields=["name", "is_active"])
            category_map[slug] = category

        now = timezone.now()
        posts = [
            {
                "slug": "what-makes-a-website-ready",
                "category": "website-tips",
                "published_at": now - timedelta(days=30),
                "title": build_translations(
                    "What makes a website ready?",
                    "Wat maakt een website klaar?",
                ),
                "excerpt": build_translations(
                    "A ready website is clear, fast, and built to guide visitors to one action. Here is the simple checklist we use.",
                    "Een goede website is duidelijk, snel en stuurt bezoekers naar een actie. Dit is de checklist die wij gebruiken.",
                ),
                "body": build_translations(
                    "When people say they need a website, they often mean they need clarity. A ready website is not the biggest or the flashiest. It is the site that lets a visitor understand your offer in a few seconds, trust you, and know what to do next. That is the difference between a site that looks nice and a site that works.\n\n"
                    "At Just Code Works we use a simple checklist before we call a site ready. First, the message is obvious. The headline tells people what you do, who it is for, and the main benefit. Second, the structure is simple. Visitors can scan the page and find services, proof, and contact details without hunting. Third, the page loads fast on mobile. Most local customers will open your site on a phone, so speed is not optional.\n\n"
                    "Next, the call to action is strong and repeated. If you want calls, give a clear call button. If you want bookings, show a direct booking path. People should not have to guess. We also check trust signals. A few reviews, logos, or real photos go a long way. They do not need to be perfect. They need to feel real.\n\n"
                    "Finally, the basics of visibility are in place. Proper headings, readable text, and a clear page title help search engines. You do not need advanced SEO to start, but you do need a clean structure. If your site does these things, it is ready. You can always add more pages, blog posts, or features later. Ready means the foundation is solid and your visitors can take action today.",
                    "Wanneer mensen zeggen dat ze een website nodig hebben, bedoelen ze vaak dat ze duidelijkheid nodig hebben. Een goede website is niet de grootste of de meest flitsende. Het is de site die in enkele seconden laat zien wat je aanbiedt, vertrouwen wekt en duidelijk maakt wat de volgende stap is.\n\n"
                    "Bij Just Code Works gebruiken we een eenvoudige checklist. Eerst moet de boodschap meteen duidelijk zijn. De kop vertelt wat je doet, voor wie het is en wat het belangrijkste voordeel is. Daarna komt de structuur. Bezoekers moeten kunnen scannen en snel diensten, bewijs en contact zien. Vervolgens is snelheid belangrijk. De meeste lokale klanten bezoeken je site via hun telefoon, dus laden moet snel gaan.\n\n"
                    "Ook de actieknop moet sterk en herhaald zijn. Als je telefoontjes wilt, maak dan een belknop. Als je boekingen wilt, geef een directe route. Mensen mogen niet hoeven raden. Daarna kijken we naar vertrouwen. Een paar reviews, fotos of echte projecten helpen enorm. Ze hoeven niet perfect te zijn, maar wel echt.\n\n"
                    "Tot slot zorgen we voor de basis van vindbaarheid. Goede koppen, leesbare teksten en een duidelijke paginatitel helpen zoekmachines. Je hebt geen ingewikkelde SEO nodig om te starten, maar wel een schone structuur. Als je site deze punten haalt, is hij klaar. De rest kan later, wanneer je groeit.",
                ),
            },
            {
                "slug": "visibility-basics-how-customers-find-you",
                "category": "visibility-seo",
                "published_at": now - timedelta(days=21),
                "title": build_translations(
                    "Visibility basics: how customers actually find you",
                    "Zichtbaarheid basics: hoe klanten je echt vinden",
                ),
                "excerpt": build_translations(
                    "Most customers do not search for your brand name. They search for a problem. This is how to show up in those moments.",
                    "De meeste klanten zoeken niet op je bedrijfsnaam maar op een probleem. Zo zorg je dat je zichtbaar bent.",
                ),
                "body": build_translations(
                    "Visibility is not magic. It is the result of clear information in the right places. Most small businesses get new customers from a short list of sources: word of mouth, Google search, maps, and social profiles. Your website is the hub that makes these sources work together.\n\n"
                    "Start with the basics: your business name, location, and services should be written in plain language. If you are a plumber, say plumber. If you are a bakery, say bakery. People search for those words. Add your city or neighborhood so the search engines know where you operate.\n\n"
                    "Next, make sure the important pages are easy to understand. A simple services section with short descriptions helps both people and search engines. Avoid long jargon. Write like you speak. Then add a clear call to action and your contact details. This turns visibility into real requests.\n\n"
                    "Images help too, but only when they have context. A photo of your team, your workspace, or your product builds trust. Add a short line near the photo explaining what it is. That is more valuable than a perfect stock image.\n\n"
                    "Finally, keep your site alive. A simple blog post or update every month is enough. It shows you are active, and it gives search engines new content to index. You do not need to chase every keyword. You just need to stay consistent. That is how visibility grows over time.",
                    "Zichtbaarheid is geen magie. Het ontstaat door duidelijke informatie op de juiste plekken. De meeste kleine bedrijven krijgen klanten via mond tot mond, Google, maps en social profielen. Je website is de plek waar alles samenkomt.\n\n"
                    "Begin met de basis. Je bedrijfsnaam, locatie en diensten moeten in gewone taal staan. Als je een loodgieter bent, schrijf loodgieter. Als je een bakkerij bent, schrijf bakkerij. Mensen zoeken op die woorden. Voeg je stad of wijk toe zodat zoekmachines weten waar je actief bent.\n\n"
                    "Maak daarna je belangrijkste onderdelen makkelijk te begrijpen. Een eenvoudige diensten sectie met korte beschrijvingen helpt zowel bezoekers als zoekmachines. Vermijd vakjargon. Schrijf zoals je praat. Voeg dan een duidelijke actieknop en contactgegevens toe. Dat zet zichtbaarheid om in aanvragen.\n\n"
                    "Beelden helpen ook, maar alleen met context. Een foto van je team, werkplaats of producten wekt vertrouwen. Zet er een korte zin bij zodat mensen weten wat ze zien. Dat is beter dan een perfect stockbeeld.\n\n"
                    "Tot slot: houd je site levend. Een simpele blogpost of update per maand is al genoeg. Het laat zien dat je actief bent en geeft zoekmachines nieuwe content. Je hoeft niet achter elke zoekterm aan. Je moet vooral consistent blijven.",
                ),
            },
            {
                "slug": "printlab-from-idea-to-delivery",
                "category": "printlab",
                "published_at": now - timedelta(days=14),
                "title": build_translations(
                    "PrintLab: from idea to delivery (how it will work)",
                    "PrintLab: van idee tot levering (zo werkt het)",
                ),
                "excerpt": build_translations(
                    "PrintLab connects your design with reliable production and delivery. Here is the simple flow we are building.",
                    "PrintLab koppelt je ontwerp aan productie en levering. Dit is de eenvoudige flow die we bouwen.",
                ),
                "body": build_translations(
                    "PrintLab is our simple print service for small businesses. The goal is to make professional print items as easy as ordering a coffee. You tell us what you need, we handle the production and delivery, and you get the result without the usual hassle.\n\n"
                    "The flow starts with a clear choice. Pick a category like cards, flyers, clothing, or merch. Then select a product and size. If you already have a design, you can upload it. If you do not, you can ask for help and we will prepare a clean layout for you.\n\n"
                    "Once the design is ready, we send a short proof for approval. This step keeps quality high and avoids surprises. After you approve, we produce the items and ship them quickly. You get updates along the way so you always know the status.\n\n"
                    "Why are we building this? Because printing is still a pain for many local businesses. Prices are unclear, tools are scattered, and support is slow. PrintLab removes the guessing. Clear pricing, clear steps, and one place for help.\n\n"
                    "We are starting with the most common items and will expand based on what you ask for. If you need something specific, tell us. The goal is not to offer everything at once, but to do the essential items very well. That is PrintLab: simple, reliable, and connected to the rest of your JCW tools.",
                    "PrintLab is onze eenvoudige printservice voor kleine bedrijven. Het doel is professioneel drukwerk net zo makkelijk te maken als koffie bestellen. Jij zegt wat je nodig hebt, wij regelen productie en levering, en jij krijgt het resultaat zonder gedoe.\n\n"
                    "De flow begint met een duidelijke keuze. Kies een categorie zoals kaarten, flyers, kleding of merch. Daarna selecteer je het product en formaat. Heb je al een ontwerp, dan upload je het. Heb je dat niet, dan vraag je hulp en maken wij een strakke layout.\n\n"
                    "Als het ontwerp klaar is sturen we een korte proef ter goedkeuring. Dit houdt de kwaliteit hoog en voorkomt verrassingen. Na je akkoord produceren we en sturen we snel op. Je krijgt updates zodat je altijd weet waar het staat.\n\n"
                    "Waarom bouwen we dit? Omdat printen voor veel lokale bedrijven nog steeds lastig is. Prijzen zijn onduidelijk, tools zijn verspreid en support duurt lang. PrintLab haalt het giswerk weg. Duidelijke prijzen, duidelijke stappen en een plek voor hulp.\n\n"
                    "We starten met de meest gebruikte items en breiden uit op basis van wat jullie vragen. Heb je iets specifieks nodig, laat het weten. Het doel is niet alles in een keer, maar de belangrijke items heel goed doen. Dat is PrintLab: simpel, betrouwbaar en verbonden met je JCW tools.",
                ),
            },
            {
                "slug": "just-code-works-roadmap-whats-coming-next",
                "category": "updates",
                "published_at": now - timedelta(days=7),
                "title": build_translations(
                    "Just Code Works roadmap: what is coming next",
                    "Just Code Works roadmap: wat er hierna komt",
                ),
                "excerpt": build_translations(
                    "We are focusing on speed, clarity, and tools that remove friction. Here is the short roadmap for the next releases.",
                    "We focussen op snelheid, duidelijkheid en tools zonder gedoe. Dit is de korte roadmap voor de komende releases.",
                ),
                "body": build_translations(
                    "We build Just Code Works for busy owners who want to get online without learning a new profession. That idea shapes our roadmap. The next releases focus on three things: faster launches, clearer content flows, and tools that remove manual work.\n\n"
                    "First, faster launches. We are simplifying the onboarding so you can answer a few questions and get a solid draft in minutes. The goal is not a perfect first version, but a strong starting point that we can refine together.\n\n"
                    "Second, clearer content. We are expanding the website templates so common businesses like salons, restaurants, and local services get better starting sections. Each template will include short prompts that help you write confident text. You will spend less time staring at a blank screen.\n\n"
                    "Third, connected tools. PrintLab is a big part of this, and we are also adding simple request and booking options. These will be easy to add without complex setup. You should be able to test what works and upgrade only when needed.\n\n"
                    "We will keep sharing progress in this blog. If you want to influence what we build next, send feedback or request a feature. JCW grows by listening to real businesses. That is the roadmap: small steps, clear wins, and steady improvements.",
                    "We bouwen Just Code Works voor ondernemers die snel online willen zonder een nieuw vak te leren. Dat idee bepaalt onze roadmap. De volgende releases draaien om drie dingen: sneller live, duidelijke content en tools die handwerk wegnemen.\n\n"
                    "Eerst sneller live gaan. We vereenvoudigen de onboarding zodat je met een paar vragen in minuten een sterke draft krijgt. Het doel is niet een perfecte eerste versie, maar een goede start die we samen verbeteren.\n\n"
                    "Daarna duidelijkere content. We breiden templates uit zodat veel voorkomende bedrijven, zoals salons, restaurants en lokale services, betere startsecties krijgen. Elke template krijgt korte prompts die helpen met tekst. Je hoeft niet langer naar een leeg scherm te kijken.\n\n"
                    "Tot slot verbonden tools. PrintLab is een groot onderdeel, en we voegen ook eenvoudige aanvraag en booking opties toe. Die zijn makkelijk aan te zetten zonder complexe instellingen. Je kunt testen wat werkt en later upgraden als dat nodig is.\n\n"
                    "We delen de voortgang hier in de blog. Wil je invloed op wat we bouwen, stuur feedback of vraag een feature aan. JCW groeit door te luisteren naar echte bedrijven. Dat is de roadmap: kleine stappen, duidelijke wins en constante verbetering.",
                ),
            },
        ]

        for post in posts:
            category = category_map[post["category"]]
            blog_post, created = BlogPost.objects.get_or_create(
                slug=post["slug"],
                defaults={
                    "title": post["title"],
                    "excerpt": post["excerpt"],
                    "body": post["body"],
                    "category": category,
                    "is_published": True,
                    "published_at": post["published_at"],
                },
            )
            if not created:
                blog_post.title = post["title"]
                blog_post.excerpt = post["excerpt"]
                blog_post.body = post["body"]
                blog_post.category = category
                blog_post.is_published = True
                blog_post.published_at = post["published_at"]
                blog_post.save()

        self.stdout.write(self.style.SUCCESS("Seeded blog categories and posts."))
