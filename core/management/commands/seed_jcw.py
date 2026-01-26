from django.core.management.base import BaseCommand

from core.models import (
    Feature,
    HeroParticlesSettings,
    Page,
    PageSection,
    Plan,
    PlanFeature,
    RightSidebarPanel,
    SectionContent,
)


class Command(BaseCommand):
    help = "Seed initial JCW pages and multilingual section content."

    def handle(self, *args, **options):
        languages = ["nl", "en", "fr", "de", "es", "pt"]

        home_translations = {
            "en": {
                "title": "JustCodeWorks",
                "nav_label": "Home",
                "meta_title": "JustCodeWorks",
                "meta_description": "Website builder and content management platform",
                "hero": {
                    "heading": "Everything you need to get your business online.",
                    "subheading": "Websites, print, POS and AI in one place.",
                    "cta_primary_text": "Start designing",
                    "cta_secondary_text": "Card Payments",
                    "body": "Printing",
                },
                "cards": [
                    {
                        "heading": "Perfect for simple local businesses",
                        "body": "Great for a few services on one page.",
                    },
                    {
                        "heading": "Grow with dedicated pages",
                        "body": "Separate pages for services, projects and more.",
                    },
                    {
                        "heading": "Sell with a simple store",
                        "body": "Take payments and manage orders easily.",
                    },
                ],
            },
            "nl": {
                "title": "JustCodeWorks",
                "nav_label": "Home",
                "meta_title": "JustCodeWorks",
                "meta_description": "Websitebouwer en contentmanagementplatform",
                "hero": {
                    "heading": "Alles om je bedrijf online te brengen.",
                    "subheading": "Websites, print, POS en AI op een plek.",
                    "cta_primary_text": "Start met ontwerpen",
                    "cta_secondary_text": "POS-systemen",
                    "body": "Drukwerk",
                },
                "cards": [
                    {
                        "heading": "Perfect voor lokale bedrijven",
                        "body": "Ideaal voor een paar diensten op een pagina.",
                    },
                    {
                        "heading": "Groei met aparte pagina's",
                        "body": "Pagina's voor diensten, projecten en meer.",
                    },
                    {
                        "heading": "Verkoop met een eenvoudige shop",
                        "body": "Accepteer betalingen en beheer orders.",
                    },
                ],
            },
            "fr": {
                "title": "JustCodeWorks",
                "nav_label": "Accueil",
                "meta_title": "JustCodeWorks",
                "meta_description": "Creation de sites et gestion de contenu",
                "hero": {
                    "heading": "Tout pour mettre votre entreprise en ligne.",
                    "subheading": "Sites web, impression, POS et IA au meme endroit.",
                    "cta_primary_text": "Commencer la creation",
                    "cta_secondary_text": "Systemes de caisse",
                    "body": "Impression",
                },
                "cards": [
                    {
                        "heading": "Parfait pour les petites entreprises",
                        "body": "Quelques services sur une seule page.",
                    },
                    {
                        "heading": "Evoluez avec des pages dediees",
                        "body": "Pages pour services, projets et plus.",
                    },
                    {
                        "heading": "Vendez avec une boutique simple",
                        "body": "Paiements et commandes faciles.",
                    },
                ],
            },
            "de": {
                "title": "JustCodeWorks",
                "nav_label": "Start",
                "meta_title": "JustCodeWorks",
                "meta_description": "Website-Builder und Content-Management",
                "hero": {
                    "heading": "Alles fuer Ihren Online-Start.",
                    "subheading": "Websites, Druck, POS und KI an einem Ort.",
                    "cta_primary_text": "Mit Design starten",
                    "cta_secondary_text": "POS-Systeme",
                    "body": "Druck",
                },
                "cards": [
                    {
                        "heading": "Perfekt fuer lokale Betriebe",
                        "body": "Wenige Leistungen auf einer Seite.",
                    },
                    {
                        "heading": "Wachsen mit eigenen Seiten",
                        "body": "Seiten fuer Leistungen und Projekte.",
                    },
                    {
                        "heading": "Verkaufen mit einfachem Shop",
                        "body": "Zahlungen und Bestellungen im Griff.",
                    },
                ],
            },
            "es": {
                "title": "JustCodeWorks",
                "nav_label": "Inicio",
                "meta_title": "JustCodeWorks",
                "meta_description": "Creador web y gestion de contenidos",
                "hero": {
                    "heading": "Todo para llevar tu negocio a internet.",
                    "subheading": "Websites, impresion, POS e IA en un solo lugar.",
                    "cta_primary_text": "Empezar a disenar",
                    "cta_secondary_text": "Sistemas POS",
                    "body": "Impresion",
                },
                "cards": [
                    {
                        "heading": "Perfecto para negocios locales",
                        "body": "Pocos servicios en una sola pagina.",
                    },
                    {
                        "heading": "Crece con paginas dedicadas",
                        "body": "Paginas para servicios y proyectos.",
                    },
                    {
                        "heading": "Vende con una tienda simple",
                        "body": "Pagos y pedidos sin complicaciones.",
                    },
                ],
            },
            "pt": {
                "title": "JustCodeWorks",
                "nav_label": "Inicio",
                "meta_title": "JustCodeWorks",
                "meta_description": "Construtor de sites e gestao de conteudos",
                "hero": {
                    "heading": "Tudo para colocar o seu negocio online.",
                    "subheading": "Websites, impressao, POS e IA num so lugar.",
                    "cta_primary_text": "Comecar a desenhar",
                    "cta_secondary_text": "Sistemas POS",
                    "body": "Impressao",
                },
                "cards": [
                    {
                        "heading": "Perfeito para negocios locais",
                        "body": "Alguns servicos numa pagina.",
                    },
                    {
                        "heading": "Cresca com paginas dedicadas",
                        "body": "Paginas para servicos e projetos.",
                    },
                    {
                        "heading": "Venda com uma loja simples",
                        "body": "Pagamentos e encomendas faceis.",
                    },
                ],
            },
        }

        page, _ = Page.objects.get_or_create(
            slug="home",
            defaults={"is_active": True, "template_key": "home"},
        )
        if not page.template_key:
            page.template_key = "home"
            page.save(update_fields=["template_key"])

        for lang in languages:
            data = home_translations[lang]
            page.set_current_language(lang)
            page.title = data["title"]
            page.nav_label = data["nav_label"]
            page.meta_title = data["meta_title"]
            page.meta_description = data["meta_description"]
            page.meta_robots_index = True
            page.meta_robots_follow = True
            page.save()

        hero_section, _ = PageSection.objects.get_or_create(
            page=page,
            key="hero",
            defaults={"order": 1, "is_visible": True},
        )
        if hero_section.order != 1:
            hero_section.order = 1
            hero_section.save(update_fields=["order"])
        hero_content, _ = SectionContent.objects.get_or_create(section=hero_section)

        card_sections = []
        for index, key in enumerate(
            ["feature_card_1", "feature_card_2", "feature_card_3"], start=2
        ):
            section, _ = PageSection.objects.get_or_create(
                page=page,
                key=key,
                defaults={"order": index, "is_visible": True},
            )
            if section.order != index:
                section.order = index
                section.save(update_fields=["order"])
            content, _ = SectionContent.objects.get_or_create(section=section)
            card_sections.append(content)

        for lang in languages:
            data = home_translations[lang]
            hero_content.set_current_language(lang)
            hero_content.heading = data["hero"]["heading"]
            hero_content.subheading = data["hero"]["subheading"]
            hero_content.body = data["hero"]["body"]
            hero_content.cta_primary_text = data["hero"]["cta_primary_text"]
            hero_content.cta_secondary_text = data["hero"]["cta_secondary_text"]
            hero_content.save()

        for idx, content in enumerate(card_sections):
            content.set_current_language(lang)
            content.heading = data["cards"][idx]["heading"]
            content.body = data["cards"][idx]["body"]
            content.save()

        solutions_card_sections = []
        for index, key in enumerate(
            [
                "solution_card_1",
                "solution_card_2",
                "solution_card_3",
                "solution_card_4",
                "solution_card_5",
                "solution_card_6",
            ],
            start=5,
        ):
            section, _ = PageSection.objects.get_or_create(
                page=page,
                key=key,
                defaults={"order": index, "is_visible": True},
            )
            if section.order != index:
                section.order = index
                section.save(update_fields=["order"])
            content, _ = SectionContent.objects.get_or_create(section=section)
            solutions_card_sections.append(content)

        solutions_cards = {
            "en": [
                {
                    "title": "Multi Page SEO",
                    "subtitle": "Multi-page site and SEO foundations",
                    "url": "core:websites_multi_page_seo",
                    "cta": "View option",
                },
                {
                    "title": "Catalog Websites",
                    "subtitle": "Showcase products, optional prices, no checkout",
                    "url": "core:websites_catalog_site",
                    "cta": "View option",
                },
                {
                    "title": "Custom Websites",
                    "subtitle": "Built to your requirements",
                    "url": "core:websites_custom",
                    "cta": "View option",
                },
                {
                    "title": "Starter eStore",
                    "subtitle": "One-page shop up to 8 products",
                    "url": "core:websites_eshop_starter",
                    "cta": "View option",
                },
                {
                    "title": "Premium eStores",
                    "subtitle": "All features, built to scale",
                    "url": "core:websites_eshop_premium",
                    "cta": "View option",
                },
                {
                    "title": "Not sure yet?",
                    "subtitle": "Tell us what you need and we will recommend the best option",
                    "url": "core:websites",
                    "cta": "Get a recommendation",
                },
            ],
            "nl": [
                {
                    "title": "Multi Page SEO",
                    "subtitle": "Multi-page site met SEO basis",
                    "url": "core:websites_multi_page_seo",
                    "cta": "Bekijk optie",
                },
                {
                    "title": "Catalogus websites",
                    "subtitle": "Producten tonen, prijzen optioneel, geen checkout",
                    "url": "core:websites_catalog_site",
                    "cta": "Bekijk optie",
                },
                {
                    "title": "Custom websites",
                    "subtitle": "Gebouwd op jouw eisen",
                    "url": "core:websites_custom",
                    "cta": "Bekijk optie",
                },
                {
                    "title": "Starter eStore",
                    "subtitle": "One-page shop tot 8 producten",
                    "url": "core:websites_eshop_starter",
                    "cta": "Bekijk optie",
                },
                {
                    "title": "Premium eStores",
                    "subtitle": "Alle features, gebouwd om te schalen",
                    "url": "core:websites_eshop_premium",
                    "cta": "Bekijk optie",
                },
                {
                    "title": "Nog niet zeker?",
                    "subtitle": "Vertel wat je nodig hebt en we adviseren",
                    "url": "core:websites",
                    "cta": "Krijg advies",
                },
            ],
            "fr": [
                {
                    "title": "Multi Page SEO",
                    "subtitle": "Site multi pages avec base SEO",
                    "url": "core:websites_multi_page_seo",
                    "cta": "Voir option",
                },
                {
                    "title": "Sites catalogue",
                    "subtitle": "Produits visibles, prix optionnels, pas de checkout",
                    "url": "core:websites_catalog_site",
                    "cta": "Voir option",
                },
                {
                    "title": "Sites sur mesure",
                    "subtitle": "Construit selon vos besoins",
                    "url": "core:websites_custom",
                    "cta": "Voir option",
                },
                {
                    "title": "eStore starter",
                    "subtitle": "Boutique one page jusqu a 8 produits",
                    "url": "core:websites_eshop_starter",
                    "cta": "Voir option",
                },
                {
                    "title": "eStores premium",
                    "subtitle": "Toutes les fonctions, evolutif",
                    "url": "core:websites_eshop_premium",
                    "cta": "Voir option",
                },
                {
                    "title": "Pas encore sur?",
                    "subtitle": "Dites ce dont vous avez besoin et on conseille",
                    "url": "core:websites",
                    "cta": "Obtenir une reco",
                },
            ],
            "de": [
                {
                    "title": "Multi Page SEO",
                    "subtitle": "Multi-Page mit SEO Basis",
                    "url": "core:websites_multi_page_seo",
                    "cta": "Option ansehen",
                },
                {
                    "title": "Katalog Websites",
                    "subtitle": "Produkte zeigen, Preise optional, kein Checkout",
                    "url": "core:websites_catalog_site",
                    "cta": "Option ansehen",
                },
                {
                    "title": "Custom Websites",
                    "subtitle": "Nach Ihren Anforderungen",
                    "url": "core:websites_custom",
                    "cta": "Option ansehen",
                },
                {
                    "title": "Starter eStore",
                    "subtitle": "One-Page Shop bis 8 Produkte",
                    "url": "core:websites_eshop_starter",
                    "cta": "Option ansehen",
                },
                {
                    "title": "Premium eStores",
                    "subtitle": "Alle Features, skalierbar",
                    "url": "core:websites_eshop_premium",
                    "cta": "Option ansehen",
                },
                {
                    "title": "Noch unsicher?",
                    "subtitle": "Sagen Sie uns was Sie brauchen",
                    "url": "core:websites",
                    "cta": "Empfehlung erhalten",
                },
            ],
            "es": [
                {
                    "title": "Multi Page SEO",
                    "subtitle": "Multi pagina con base SEO",
                    "url": "core:websites_multi_page_seo",
                    "cta": "Ver opcion",
                },
                {
                    "title": "Websites catalogo",
                    "subtitle": "Mostrar productos, precios opcionales, sin checkout",
                    "url": "core:websites_catalog_site",
                    "cta": "Ver opcion",
                },
                {
                    "title": "Websites a medida",
                    "subtitle": "Construido a tus requisitos",
                    "url": "core:websites_custom",
                    "cta": "Ver opcion",
                },
                {
                    "title": "Starter eStore",
                    "subtitle": "Tienda one page hasta 8 productos",
                    "url": "core:websites_eshop_starter",
                    "cta": "Ver opcion",
                },
                {
                    "title": "Premium eStores",
                    "subtitle": "Todas las funciones, escalable",
                    "url": "core:websites_eshop_premium",
                    "cta": "Ver opcion",
                },
                {
                    "title": "No estas seguro?",
                    "subtitle": "Dinos lo que necesitas y recomendamos",
                    "url": "core:websites",
                    "cta": "Recibir recomendacion",
                },
            ],
            "pt": [
                {
                    "title": "Multi Page SEO",
                    "subtitle": "Multi pagina com base SEO",
                    "url": "core:websites_multi_page_seo",
                    "cta": "Ver opcao",
                },
                {
                    "title": "Websites catalogo",
                    "subtitle": "Mostrar produtos, precos opcionais, sem checkout",
                    "url": "core:websites_catalog_site",
                    "cta": "Ver opcao",
                },
                {
                    "title": "Websites personalizados",
                    "subtitle": "Construido a sua medida",
                    "url": "core:websites_custom",
                    "cta": "Ver opcao",
                },
                {
                    "title": "Starter eStore",
                    "subtitle": "Loja one page ate 8 produtos",
                    "url": "core:websites_eshop_starter",
                    "cta": "Ver opcao",
                },
                {
                    "title": "Premium eStores",
                    "subtitle": "Todas as funcoes, escalavel",
                    "url": "core:websites_eshop_premium",
                    "cta": "Ver opcao",
                },
                {
                    "title": "Ainda nao tem certeza?",
                    "subtitle": "Diga o que precisa e recomendamos",
                    "url": "core:websites",
                    "cta": "Receber recomendacao",
                },
            ],
        }

        for lang in languages:
            cards = solutions_cards[lang]
            for idx, content in enumerate(solutions_card_sections):
                card = cards[idx]
                content.set_current_language(lang)
                content.heading = card["title"]
                content.body = card["subtitle"]
                content.cta_primary_text = card["cta"]
                content.cta_primary_url = card["url"]
                content.save()

        page_translations = {
            "websites": {
                "en": {
                    "title": "Websites",
                    "nav_label": "Websites",
                    "meta_title": "Websites",
                    "meta_description": "Web design and development for small businesses.",
                    "hero": {
                        "heading": "Websites that work as hard as you do.",
                        "subheading": "Choose the type of website that fits your business today.",
                        "cta_primary_text": "Start building",
                        "cta_secondary_text": "View demo",
                    },
                    "main": {
                        "heading": "Choose your perfect solution",
                        "body": "From one-page sites to online stores.",
                    },
                    "cta": {"cta_primary_text": "Start building now"},
                },
                "nl": {
                    "title": "Websites",
                    "nav_label": "Websites",
                    "meta_title": "Websites",
                    "meta_description": "Webdesign en ontwikkeling voor kleine bedrijven.",
                    "hero": {
                        "heading": "Websites die net zo hard werken als jij.",
                        "subheading": "Kies het type website dat vandaag bij je past.",
                        "cta_primary_text": "Start met bouwen",
                        "cta_secondary_text": "Bekijk demo",
                    },
                    "main": {
                        "heading": "Kies jouw oplossing",
                        "body": "Van one-pagers tot webshops.",
                    },
                    "cta": {"cta_primary_text": "Start nu"},
                },
                "fr": {
                    "title": "Sites web",
                    "nav_label": "Sites web",
                    "meta_title": "Sites web",
                    "meta_description": "Creation de sites web pour petites entreprises.",
                    "hero": {
                        "heading": "Des sites web qui travaillent pour vous.",
                        "subheading": "Choisissez le type de site adapte a votre activite.",
                        "cta_primary_text": "Commencer",
                        "cta_secondary_text": "Voir la demo",
                    },
                    "main": {
                        "heading": "Choisissez la bonne solution",
                        "body": "Du site vitrine a la boutique en ligne.",
                    },
                    "cta": {"cta_primary_text": "Demarrer"},
                },
                "de": {
                    "title": "Websites",
                    "nav_label": "Websites",
                    "meta_title": "Websites",
                    "meta_description": "Webdesign und Entwicklung fuer kleine Unternehmen.",
                    "hero": {
                        "heading": "Websites, die fuer Sie arbeiten.",
                        "subheading": "Waehlen Sie den passenden Website-Typ.",
                        "cta_primary_text": "Jetzt starten",
                        "cta_secondary_text": "Demo ansehen",
                    },
                    "main": {
                        "heading": "Die passende Loesung",
                        "body": "Von One-Pagern bis Onlineshops.",
                    },
                    "cta": {"cta_primary_text": "Jetzt starten"},
                },
                "es": {
                    "title": "Websites",
                    "nav_label": "Websites",
                    "meta_title": "Websites",
                    "meta_description": "Diseno y desarrollo web para pequenos negocios.",
                    "hero": {
                        "heading": "Websites que trabajan para ti.",
                        "subheading": "Elige el tipo de web que encaja hoy.",
                        "cta_primary_text": "Empezar",
                        "cta_secondary_text": "Ver demo",
                    },
                    "main": {
                        "heading": "Elige tu solucion",
                        "body": "Desde paginas simples hasta tiendas online.",
                    },
                    "cta": {"cta_primary_text": "Empezar ahora"},
                },
                "pt": {
                    "title": "Websites",
                    "nav_label": "Websites",
                    "meta_title": "Websites",
                    "meta_description": "Design e desenvolvimento web para pequenos negocios.",
                    "hero": {
                        "heading": "Websites que trabalham por si.",
                        "subheading": "Escolha o tipo de site certo hoje.",
                        "cta_primary_text": "Comecar",
                        "cta_secondary_text": "Ver demo",
                    },
                    "main": {
                        "heading": "Escolha a solucao",
                        "body": "De one-pagers a lojas online.",
                    },
                    "cta": {"cta_primary_text": "Comecar agora"},
                },
            },
            "services": {
                "en": {
                    "title": "Services",
                    "nav_label": "Services",
                    "meta_title": "Services",
                    "meta_description": "Design, development, print, and support services.",
                    "hero": {
                        "heading": "Services that keep your business moving.",
                        "subheading": "Design, development, printing, and support in one place.",
                        "cta_primary_text": "Explore services",
                        "cta_secondary_text": "Get a quote",
                    },
                    "main": {
                        "heading": "What we can do for you",
                        "body": "Websites, apps, print materials, and maintenance.",
                    },
                    "cta": {"cta_primary_text": "Talk to us"},
                },
                "nl": {
                    "title": "Diensten",
                    "nav_label": "Diensten",
                    "meta_title": "Diensten",
                    "meta_description": "Design, ontwikkeling, drukwerk en support.",
                    "hero": {
                        "heading": "Diensten die je bedrijf vooruit helpen.",
                        "subheading": "Design, ontwikkeling, drukwerk en support op een plek.",
                        "cta_primary_text": "Bekijk diensten",
                        "cta_secondary_text": "Vraag offerte",
                    },
                    "main": {
                        "heading": "Wat we voor je kunnen doen",
                        "body": "Websites, apps, drukwerk en onderhoud.",
                    },
                    "cta": {"cta_primary_text": "Neem contact op"},
                },
                "fr": {
                    "title": "Services",
                    "nav_label": "Services",
                    "meta_title": "Services",
                    "meta_description": "Design, developpement, impression et support.",
                    "hero": {
                        "heading": "Des services pour avancer.",
                        "subheading": "Design, developpement, impression et support au meme endroit.",
                        "cta_primary_text": "Voir les services",
                        "cta_secondary_text": "Demander un devis",
                    },
                    "main": {
                        "heading": "Ce que nous faisons",
                        "body": "Sites web, apps, supports imprimes et maintenance.",
                    },
                    "cta": {"cta_primary_text": "Parlons-en"},
                },
                "de": {
                    "title": "Services",
                    "nav_label": "Services",
                    "meta_title": "Services",
                    "meta_description": "Design, Entwicklung, Druck und Support.",
                    "hero": {
                        "heading": "Services, die Ihr Geschaeft voranbringen.",
                        "subheading": "Design, Entwicklung, Druck und Support an einem Ort.",
                        "cta_primary_text": "Services ansehen",
                        "cta_secondary_text": "Angebot anfordern",
                    },
                    "main": {
                        "heading": "Was wir fuer Sie tun",
                        "body": "Websites, Apps, Druckmaterialien und Wartung.",
                    },
                    "cta": {"cta_primary_text": "Kontakt aufnehmen"},
                },
                "es": {
                    "title": "Servicios",
                    "nav_label": "Servicios",
                    "meta_title": "Servicios",
                    "meta_description": "Diseno, desarrollo, impresion y soporte.",
                    "hero": {
                        "heading": "Servicios que impulsan tu negocio.",
                        "subheading": "Diseno, desarrollo, impresion y soporte en un solo lugar.",
                        "cta_primary_text": "Ver servicios",
                        "cta_secondary_text": "Pedir presupuesto",
                    },
                    "main": {
                        "heading": "Lo que hacemos",
                        "body": "Websites, apps, material impreso y mantenimiento.",
                    },
                    "cta": {"cta_primary_text": "Hablemos"},
                },
                "pt": {
                    "title": "Servicos",
                    "nav_label": "Servicos",
                    "meta_title": "Servicos",
                    "meta_description": "Design, desenvolvimento, impressao e suporte.",
                    "hero": {
                        "heading": "Servicos que fazem o seu negocio avancar.",
                        "subheading": "Design, desenvolvimento, impressao e suporte num so lugar.",
                        "cta_primary_text": "Ver servicos",
                        "cta_secondary_text": "Pedir orcamento",
                    },
                    "main": {
                        "heading": "O que fazemos",
                        "body": "Websites, apps, impressos e manutencao.",
                    },
                    "cta": {"cta_primary_text": "Fale connosco"},
                },
            },
            "pos-systems": {
                "en": {
                    "title": "Card Payments",
                    "nav_label": "Card Payments",
                    "meta_title": "Card Payments",
                    "meta_description": "POS systems and partner recommendations for retail, hospitality, and services.",
                    "hero": {
                        "heading": "POS systems that make checkout easy",
                        "subheading": "We help you choose a reliable POS that fits your business. Simple, clear, and practical.",
                        "cta_primary_text": "Get a recommendation",
                        "cta_secondary_text": "Browse partners",
                    },
                    "main": {
                        "heading": "Find the right POS for your business",
                        "body": "Retail, hospitality, and services each need different workflows. We highlight practical options and how they fit.",
                    },
                    "cta": {
                        "heading": "Need help choosing?",
                        "body": "Tell us your business type and we will suggest options.",
                        "cta_primary_text": "Get a recommendation",
                        "cta_primary_url": "/help-center/",
                    },
                    "pos_category_cards": [
                        {
                            "heading": "Retail POS",
                            "subheading": "Best for shops and boutiques",
                            "bullets": ["Fast checkout", "Barcode-ready", "Simple inventory"],
                            "cta_primary_text": "View retail options",
                            "cta_primary_url": "/pos-systems/retail/",
                        },
                        {
                            "heading": "Hospitality POS",
                            "subheading": "Best for cafes, bars, and restaurants",
                            "bullets": ["Tables & split bills", "Kitchen tickets", "Tip-friendly"],
                            "cta_primary_text": "View hospitality options",
                            "cta_primary_url": "/pos-systems/hospitality/",
                        },
                        {
                            "heading": "Services POS",
                            "subheading": "Best for bookings and invoices",
                            "bullets": ["Appointments", "Invoices/receipts", "Optional deposits"],
                            "cta_primary_text": "View service options",
                            "cta_primary_url": "/pos-systems/services/",
                        },
                    ],
                },
                "nl": {
                    "title": "POS-systemen",
                    "nav_label": "POS-systemen",
                    "meta_title": "POS-systemen",
                    "meta_description": "POS systemen en partners voor retail, horeca en services.",
                    "hero": {
                        "heading": "POS systemen die afrekenen eenvoudig maken",
                        "subheading": "We helpen je een betrouwbare POS te kiezen. Simpel, duidelijk en praktisch.",
                        "cta_primary_text": "Krijg advies",
                        "cta_secondary_text": "Bekijk partners",
                    },
                    "main": {
                        "heading": "Vind de juiste POS voor jouw bedrijf",
                        "body": "Retail, horeca en services hebben andere workflows. We tonen praktische opties en wat past.",
                    },
                    "cta": {
                        "heading": "Hulp nodig bij kiezen?",
                        "body": "Vertel je type bedrijf en wij geven opties.",
                        "cta_primary_text": "Krijg advies",
                        "cta_primary_url": "/help-center/",
                    },
                    "pos_category_cards": [
                        {
                            "heading": "Retail POS",
                            "subheading": "Beste voor winkels en boetieks",
                            "bullets": ["Snelle checkout", "Barcode-klaar", "Eenvoudige voorraad"],
                            "cta_primary_text": "Bekijk retail opties",
                            "cta_primary_url": "/pos-systems/retail/",
                        },
                        {
                            "heading": "Horeca POS",
                            "subheading": "Beste voor cafes, bars en restaurants",
                            "bullets": ["Tafels & split bill", "Keukenbonnen", "Fooi-vriendelijk"],
                            "cta_primary_text": "Bekijk horeca opties",
                            "cta_primary_url": "/pos-systems/hospitality/",
                        },
                        {
                            "heading": "Services POS",
                            "subheading": "Beste voor afspraken en facturen",
                            "bullets": ["Afspraken", "Facturen/bonnen", "Optionele aanbetaling"],
                            "cta_primary_text": "Bekijk service opties",
                            "cta_primary_url": "/pos-systems/services/",
                        },
                    ],
                },
                "fr": {
                    "title": "Systemes de caisse",
                    "nav_label": "Systemes de caisse",
                    "meta_title": "Systemes de caisse",
                    "meta_description": "POS et partenaires pour retail, restauration et services.",
                    "hero": {
                        "heading": "POS pour un encaissement simple",
                        "subheading": "Nous aidons a choisir un POS fiable. Simple, clair et pratique.",
                        "cta_primary_text": "Obtenir un conseil",
                        "cta_secondary_text": "Voir les partenaires",
                    },
                    "main": {
                        "heading": "Trouver le bon POS",
                        "body": "Retail, restauration et services ont des besoins differents. Nous proposons des options pratiques.",
                    },
                    "cta": {
                        "heading": "Besoin d aide pour choisir ?",
                        "body": "Dites votre activite et nous proposerons des options.",
                        "cta_primary_text": "Obtenir un conseil",
                        "cta_primary_url": "/help-center/",
                    },
                    "pos_category_cards": [
                        {
                            "heading": "POS retail",
                            "subheading": "Ideal pour boutiques",
                            "bullets": ["Encaissement rapide", "Codes-barres", "Stock simple"],
                            "cta_primary_text": "Voir options retail",
                            "cta_primary_url": "/pos-systems/retail/",
                        },
                        {
                            "heading": "POS restauration",
                            "subheading": "Ideal pour cafes, bars, restaurants",
                            "bullets": ["Tables & split bills", "Tickets cuisine", "Pourboires"],
                            "cta_primary_text": "Voir options restauration",
                            "cta_primary_url": "/pos-systems/hospitality/",
                        },
                        {
                            "heading": "POS services",
                            "subheading": "Ideal pour rendez-vous et factures",
                            "bullets": ["Rendez-vous", "Factures/reçus", "Acomptes optionnels"],
                            "cta_primary_text": "Voir options services",
                            "cta_primary_url": "/pos-systems/services/",
                        },
                    ],
                },
                "de": {
                    "title": "POS-Systeme",
                    "nav_label": "POS-Systeme",
                    "meta_title": "POS-Systeme",
                    "meta_description": "POS Systeme und Partner fuer Retail, Gastro und Services.",
                    "hero": {
                        "heading": "POS Systeme fuer einfaches Kassieren",
                        "subheading": "Wir helfen bei der Wahl eines zuverlaessigen POS. Einfach, klar, praktisch.",
                        "cta_primary_text": "Empfehlung erhalten",
                        "cta_secondary_text": "Partner ansehen",
                    },
                    "main": {
                        "heading": "Das passende POS finden",
                        "body": "Retail, Gastronomie und Services brauchen andere Ablaufe. Wir zeigen passende Optionen.",
                    },
                    "cta": {
                        "heading": "Hilfe bei der Auswahl?",
                        "body": "Nennen Sie Ihren Betrieb und wir schlagen Optionen vor.",
                        "cta_primary_text": "Empfehlung erhalten",
                        "cta_primary_url": "/help-center/",
                    },
                    "pos_category_cards": [
                        {
                            "heading": "Retail POS",
                            "subheading": "Ideal fuer Shops und Boutiquen",
                            "bullets": ["Schneller Checkout", "Barcode bereit", "Einfache Bestandsverwaltung"],
                            "cta_primary_text": "Retail Optionen ansehen",
                            "cta_primary_url": "/pos-systems/retail/",
                        },
                        {
                            "heading": "Gastro POS",
                            "subheading": "Ideal fuer Cafes, Bars, Restaurants",
                            "bullets": ["Tische & Split Bills", "Kuechenbons", "Trinkgeld"],
                            "cta_primary_text": "Gastro Optionen ansehen",
                            "cta_primary_url": "/pos-systems/hospitality/",
                        },
                        {
                            "heading": "Services POS",
                            "subheading": "Ideal fuer Termine und Rechnungen",
                            "bullets": ["Termine", "Rechnungen/Belege", "Optionale Anzahlungen"],
                            "cta_primary_text": "Service Optionen ansehen",
                            "cta_primary_url": "/pos-systems/services/",
                        },
                    ],
                },
                "es": {
                    "title": "Sistemas POS",
                    "nav_label": "Sistemas POS",
                    "meta_title": "Sistemas POS",
                    "meta_description": "POS y partners para retail, hosteleria y servicios.",
                    "hero": {
                        "heading": "POS para un cobro sencillo",
                        "subheading": "Te ayudamos a elegir un POS fiable. Simple, claro y practico.",
                        "cta_primary_text": "Obtener recomendacion",
                        "cta_secondary_text": "Ver partners",
                    },
                    "main": {
                        "heading": "Encuentra el POS adecuado",
                        "body": "Retail, hosteleria y servicios tienen flujos distintos. Mostramos opciones practicas.",
                    },
                    "cta": {
                        "heading": "Necesitas ayuda para elegir?",
                        "body": "Cuenta tu tipo de negocio y sugerimos opciones.",
                        "cta_primary_text": "Obtener recomendacion",
                        "cta_primary_url": "/help-center/",
                    },
                    "pos_category_cards": [
                        {
                            "heading": "POS retail",
                            "subheading": "Ideal para tiendas y boutiques",
                            "bullets": ["Cobro rapido", "Listo para codigos de barras", "Inventario simple"],
                            "cta_primary_text": "Ver opciones retail",
                            "cta_primary_url": "/pos-systems/retail/",
                        },
                        {
                            "heading": "POS hosteleria",
                            "subheading": "Ideal para cafes, bares y restaurantes",
                            "bullets": ["Mesas y cuentas divididas", "Tickets de cocina", "Propinas"],
                            "cta_primary_text": "Ver opciones hosteleria",
                            "cta_primary_url": "/pos-systems/hospitality/",
                        },
                        {
                            "heading": "POS servicios",
                            "subheading": "Ideal para reservas y facturas",
                            "bullets": ["Citas", "Facturas/recibos", "Depositos opcionales"],
                            "cta_primary_text": "Ver opciones servicios",
                            "cta_primary_url": "/pos-systems/services/",
                        },
                    ],
                },
                "pt": {
                    "title": "Sistemas POS",
                    "nav_label": "Sistemas POS",
                    "meta_title": "Sistemas POS",
                    "meta_description": "POS e parceiros para retalho, hotelaria e servicos.",
                    "hero": {
                        "heading": "POS para checkout simples",
                        "subheading": "Ajudamos a escolher um POS fiavel. Simples, claro e pratico.",
                        "cta_primary_text": "Pedir recomendacao",
                        "cta_secondary_text": "Ver parceiros",
                    },
                    "main": {
                        "heading": "Encontre o POS certo",
                        "body": "Retalho, hotelaria e servicos precisam de fluxos diferentes. Mostramos opcoes praticas.",
                    },
                    "cta": {
                        "heading": "Precisa de ajuda a escolher?",
                        "body": "Diga o seu tipo de negocio e sugerimos opcoes.",
                        "cta_primary_text": "Pedir recomendacao",
                        "cta_primary_url": "/help-center/",
                    },
                    "pos_category_cards": [
                        {
                            "heading": "POS retalho",
                            "subheading": "Ideal para lojas e boutiques",
                            "bullets": ["Checkout rapido", "Pronto para codigos de barras", "Stock simples"],
                            "cta_primary_text": "Ver opcoes de retalho",
                            "cta_primary_url": "/pos-systems/retail/",
                        },
                        {
                            "heading": "POS hotelaria",
                            "subheading": "Ideal para cafes, bares e restaurantes",
                            "bullets": ["Mesas e contas divididas", "Tickets de cozinha", "Gorjetas"],
                            "cta_primary_text": "Ver opcoes de hotelaria",
                            "cta_primary_url": "/pos-systems/hospitality/",
                        },
                        {
                            "heading": "POS servicos",
                            "subheading": "Ideal para marcacoes e faturas",
                            "bullets": ["Marcacoes", "Faturas/recibos", "Adiantamentos opcionais"],
                            "cta_primary_text": "Ver opcoes de servicos",
                            "cta_primary_url": "/pos-systems/services/",
                        },
                    ],
                },
            },
            "help-center": {
                "en": {
                    "title": "Help Center",
                    "nav_label": "Help Center",
                    "meta_title": "Help Center",
                    "meta_description": "Guides, FAQs, and support for JustCodeWorks.",
                    "hero": {
                        "heading": "Help Center",
                        "subheading": "Guides, FAQs, and support for everything JustCodeWorks.",
                        "cta_primary_text": "Browse help articles",
                        "cta_secondary_text": "Contact support",
                    },
                    "main": {
                        "heading": "Popular topics",
                        "body": "Getting started, billing, printing, POS and account management.",
                    },
                    "cta": {"cta_primary_text": "Get help"},
                },
                "nl": {
                    "title": "Helpcenter",
                    "nav_label": "Helpcenter",
                    "meta_title": "Helpcenter",
                    "meta_description": "Handleidingen, FAQ en support voor JustCodeWorks.",
                    "hero": {
                        "heading": "Helpcenter",
                        "subheading": "Handleidingen, FAQ en support voor JustCodeWorks.",
                        "cta_primary_text": "Bekijk artikelen",
                        "cta_secondary_text": "Contact support",
                    },
                    "main": {
                        "heading": "Populaire onderwerpen",
                        "body": "Starten, facturatie, drukwerk, POS en accountbeheer.",
                    },
                    "cta": {"cta_primary_text": "Hulp krijgen"},
                },
                "fr": {
                    "title": "Centre d'aide",
                    "nav_label": "Centre d'aide",
                    "meta_title": "Centre d'aide",
                    "meta_description": "Guides, FAQ et support JustCodeWorks.",
                    "hero": {
                        "heading": "Centre d'aide",
                        "subheading": "Guides, FAQ et support pour JustCodeWorks.",
                        "cta_primary_text": "Voir les articles",
                        "cta_secondary_text": "Contacter le support",
                    },
                    "main": {
                        "heading": "Sujets populaires",
                        "body": "Demarrage, facturation, impression, POS et compte.",
                    },
                    "cta": {"cta_primary_text": "Obtenir de l'aide"},
                },
                "de": {
                    "title": "Hilfe",
                    "nav_label": "Hilfe",
                    "meta_title": "Hilfe",
                    "meta_description": "Anleitungen, FAQ und Support fuer JustCodeWorks.",
                    "hero": {
                        "heading": "Hilfe-Center",
                        "subheading": "Anleitungen, FAQ und Support fuer JustCodeWorks.",
                        "cta_primary_text": "Artikel ansehen",
                        "cta_secondary_text": "Support kontaktieren",
                    },
                    "main": {
                        "heading": "Beliebte Themen",
                        "body": "Einstieg, Abrechnung, Druck, POS und Konto.",
                    },
                    "cta": {"cta_primary_text": "Hilfe erhalten"},
                },
                "es": {
                    "title": "Centro de ayuda",
                    "nav_label": "Centro de ayuda",
                    "meta_title": "Centro de ayuda",
                    "meta_description": "Guias, FAQ y soporte de JustCodeWorks.",
                    "hero": {
                        "heading": "Centro de ayuda",
                        "subheading": "Guias, FAQ y soporte para JustCodeWorks.",
                        "cta_primary_text": "Ver articulos",
                        "cta_secondary_text": "Contactar soporte",
                    },
                    "main": {
                        "heading": "Temas populares",
                        "body": "Inicio, facturacion, impresion, POS y cuenta.",
                    },
                    "cta": {"cta_primary_text": "Obtener ayuda"},
                },
                "pt": {
                    "title": "Centro de ajuda",
                    "nav_label": "Centro de ajuda",
                    "meta_title": "Centro de ajuda",
                    "meta_description": "Guias, FAQ e suporte da JustCodeWorks.",
                    "hero": {
                        "heading": "Centro de ajuda",
                        "subheading": "Guias, FAQ e suporte para a JustCodeWorks.",
                        "cta_primary_text": "Ver artigos",
                        "cta_secondary_text": "Contactar suporte",
                    },
                    "main": {
                        "heading": "Topicos populares",
                        "body": "Inicio, faturacao, impressao, POS e conta.",
                    },
                    "cta": {"cta_primary_text": "Pedir ajuda"},
                },
            },
            "print-lab": {
                "en": {
                    "title": "Print Lab",
                    "nav_label": "Printing",
                    "meta_title": "Print Lab",
                    "meta_description": "Business printing for cards, flyers, and branded materials.",
                    "hero": {
                        "heading": "Print Lab",
                        "subheading": "Business cards, flyers, and branded materials delivered fast.",
                        "cta_primary_text": "Start your project",
                        "cta_secondary_text": "View portfolio",
                    },
                    "main": {
                        "heading": "Print products for local businesses",
                        "body": "Cards, flyers, menus, stickers and more. White-label production and shipping by Printful.",
                    },
                    "cta": {"cta_primary_text": "Get a quote"},
                },
                "nl": {
                    "title": "Print Lab",
                    "nav_label": "Print",
                    "meta_title": "Print Lab",
                    "meta_description": "Drukwerk voor kaartjes, flyers en merkproducten.",
                    "hero": {
                        "heading": "Print Lab",
                        "subheading": "Visitekaartjes, flyers en merkdrukwerk snel geleverd.",
                        "cta_primary_text": "Start je project",
                        "cta_secondary_text": "Bekijk portfolio",
                    },
                    "main": {
                        "heading": "Print voor lokale bedrijven",
                        "body": "Kaarten, flyers, menu's, stickers en meer. White-label productie en verzending via Printful.",
                    },
                    "cta": {"cta_primary_text": "Vraag offerte"},
                },
                "fr": {
                    "title": "Print Lab",
                    "nav_label": "Impression",
                    "meta_title": "Print Lab",
                    "meta_description": "Impression pro pour cartes, flyers et supports.",
                    "hero": {
                        "heading": "Print Lab",
                        "subheading": "Cartes, flyers et supports de marque livrees rapidement.",
                        "cta_primary_text": "Lancer le projet",
                        "cta_secondary_text": "Voir le portfolio",
                    },
                    "main": {
                        "heading": "Impression pour les entreprises locales",
                        "body": "Cartes, flyers, menus, stickers et plus. Production et livraison white-label par Printful.",
                    },
                    "cta": {"cta_primary_text": "Demander un devis"},
                },
                "de": {
                    "title": "Print Lab",
                    "nav_label": "Druck",
                    "meta_title": "Print Lab",
                    "meta_description": "Druckprodukte fuer Karten, Flyer und Markenmaterial.",
                    "hero": {
                        "heading": "Print Lab",
                        "subheading": "Visitenkarten, Flyer und Markenmaterial schnell geliefert.",
                        "cta_primary_text": "Projekt starten",
                        "cta_secondary_text": "Portfolio ansehen",
                    },
                    "main": {
                        "heading": "Druck fuer lokale Unternehmen",
                        "body": "Karten, Flyer, Menues, Sticker und mehr. White-label Produktion und Versand durch Printful.",
                    },
                    "cta": {"cta_primary_text": "Angebot anfordern"},
                },
                "es": {
                    "title": "Print Lab",
                    "nav_label": "Impresion",
                    "meta_title": "Print Lab",
                    "meta_description": "Impresion profesional para tarjetas, flyers y marca.",
                    "hero": {
                        "heading": "Print Lab",
                        "subheading": "Tarjetas, flyers y material de marca con entrega rapida.",
                        "cta_primary_text": "Iniciar proyecto",
                        "cta_secondary_text": "Ver portfolio",
                    },
                    "main": {
                        "heading": "Impresion para negocios locales",
                        "body": "Tarjetas, flyers, menus, stickers y mas. Produccion y envio white-label por Printful.",
                    },
                    "cta": {"cta_primary_text": "Pedir presupuesto"},
                },
                "pt": {
                    "title": "Print Lab",
                    "nav_label": "Impressao",
                    "meta_title": "Print Lab",
                    "meta_description": "Impressao profissional para cartoes, flyers e marca.",
                    "hero": {
                        "heading": "Print Lab",
                        "subheading": "Cartoes, flyers e materiais de marca com entrega rapida.",
                        "cta_primary_text": "Iniciar projeto",
                        "cta_secondary_text": "Ver portfolio",
                    },
                    "main": {
                        "heading": "Impressao para negocios locais",
                        "body": "Cartoes, flyers, menus, autocolantes e mais. Producao e envio white-label pela Printful.",
                    },
                    "cta": {"cta_primary_text": "Pedir orcamento"},
                },
            },
            "print-lab-products": {
                "en": {
                    "title": "Print Studio Products",
                    "nav_label": "Print Studio",
                    "meta_title": "Print Studio Products",
                    "meta_description": "Product categories for Print Studio.",
                    "hero": {
                        "heading": "Print Studio products",
                        "subheading": "Cards, flyers, stickers, merch and more.",
                        "cta_primary_text": "Explore products",
                        "cta_secondary_text": "Contact support",
                    },
                    "main": {
                        "heading": "Popular categories",
                        "body": "Business cards, flyers, brochures, stickers, labels and apparel. White-label production and shipping by Printful.",
                    },
                    "cta": {"cta_primary_text": "Request samples"},
                },
                "nl": {
                    "title": "Print Studio Producten",
                    "nav_label": "Print Studio",
                    "meta_title": "Print Studio Producten",
                    "meta_description": "Productcategorieen voor Print Studio.",
                    "hero": {
                        "heading": "Print Studio producten",
                        "subheading": "Kaarten, flyers, stickers, merch en meer.",
                        "cta_primary_text": "Bekijk producten",
                        "cta_secondary_text": "Contact support",
                    },
                    "main": {
                        "heading": "Populaire categorieen",
                        "body": "Visitekaartjes, flyers, brochures, stickers, labels en kleding. White-label productie en verzending via Printful.",
                    },
                    "cta": {"cta_primary_text": "Vraag samples"},
                },
                "fr": {
                    "title": "Produits Print Studio",
                    "nav_label": "Print Studio",
                    "meta_title": "Produits Print Studio",
                    "meta_description": "Categories produits pour Print Studio.",
                    "hero": {
                        "heading": "Produits Print Studio",
                        "subheading": "Cartes, flyers, stickers, merch et plus.",
                        "cta_primary_text": "Voir les produits",
                        "cta_secondary_text": "Contacter le support",
                    },
                    "main": {
                        "heading": "Categories populaires",
                        "body": "Cartes, flyers, brochures, stickers, labels et vetements. Production et livraison white-label par Printful.",
                    },
                    "cta": {"cta_primary_text": "Demander des echantillons"},
                },
                "de": {
                    "title": "Print Studio Produkte",
                    "nav_label": "Print Studio",
                    "meta_title": "Print Studio Produkte",
                    "meta_description": "Produktkategorien fuer Print Studio.",
                    "hero": {
                        "heading": "Print Studio Produkte",
                        "subheading": "Karten, Flyer, Sticker, Merch und mehr.",
                        "cta_primary_text": "Produkte ansehen",
                        "cta_secondary_text": "Support kontaktieren",
                    },
                    "main": {
                        "heading": "Beliebte Kategorien",
                        "body": "Visitenkarten, Flyer, Broschueren, Sticker, Labels und Kleidung. White-label Produktion und Versand durch Printful.",
                    },
                    "cta": {"cta_primary_text": "Muster anfragen"},
                },
                "es": {
                    "title": "Productos Print Studio",
                    "nav_label": "Print Studio",
                    "meta_title": "Productos Print Studio",
                    "meta_description": "Categorias de productos para Print Studio.",
                    "hero": {
                        "heading": "Productos Print Studio",
                        "subheading": "Tarjetas, flyers, stickers, merch y mas.",
                        "cta_primary_text": "Ver productos",
                        "cta_secondary_text": "Contactar soporte",
                    },
                    "main": {
                        "heading": "Categorias populares",
                        "body": "Tarjetas, flyers, folletos, stickers, etiquetas y ropa. Produccion y envio white-label por Printful.",
                    },
                    "cta": {"cta_primary_text": "Solicitar muestras"},
                },
                "pt": {
                    "title": "Produtos Print Studio",
                    "nav_label": "Print Studio",
                    "meta_title": "Produtos Print Studio",
                    "meta_description": "Categorias de produtos para Print Studio.",
                    "hero": {
                        "heading": "Produtos Print Studio",
                        "subheading": "Cartoes, flyers, autocolantes, merch e mais.",
                        "cta_primary_text": "Ver produtos",
                        "cta_secondary_text": "Contactar suporte",
                    },
                    "main": {
                        "heading": "Categorias populares",
                        "body": "Cartoes, flyers, brochuras, autocolantes, etiquetas e roupa. Producao e envio white-label pela Printful.",
                    },
                    "cta": {"cta_primary_text": "Pedir amostras"},
                },
            },
            "print-lab-how-it-works": {
                "en": {
                    "title": "How Print Studio Works",
                    "nav_label": "Print Studio",
                    "meta_title": "How Print Studio Works",
                    "meta_description": "White-label flow for Print Studio.",
                    "hero": {
                        "heading": "How Print Studio works",
                        "subheading": "We run the storefront. Printful produces and ships.",
                        "cta_primary_text": "Start a print project",
                        "cta_secondary_text": "Contact support",
                    },
                    "main": {
                        "heading": "White-label fulfillment",
                        "body": "Orders go to Printful for production and shipping with your branding. Returns and defects follow Printful policy.",
                    },
                    "cta": {"cta_primary_text": "Request a quote"},
                },
                "nl": {
                    "title": "Hoe Print Studio werkt",
                    "nav_label": "Print Studio",
                    "meta_title": "Hoe Print Studio werkt",
                    "meta_description": "White-label flow voor Print Studio.",
                    "hero": {
                        "heading": "Hoe Print Studio werkt",
                        "subheading": "Wij beheren de storefront. Printful produceert en verzendt.",
                        "cta_primary_text": "Start een print project",
                        "cta_secondary_text": "Contact support",
                    },
                    "main": {
                        "heading": "White-label fulfillment",
                        "body": "Bestellingen gaan naar Printful voor productie en verzending met jouw branding. Retouren volgen Printful beleid.",
                    },
                    "cta": {"cta_primary_text": "Vraag offerte"},
                },
                "fr": {
                    "title": "Comment fonctionne Print Studio",
                    "nav_label": "Print Studio",
                    "meta_title": "Comment fonctionne Print Studio",
                    "meta_description": "Flux white-label pour Print Studio.",
                    "hero": {
                        "heading": "Comment fonctionne Print Studio",
                        "subheading": "Nous gerons la vitrine. Printful produit et expedie.",
                        "cta_primary_text": "Lancer un projet print",
                        "cta_secondary_text": "Contacter le support",
                    },
                    "main": {
                        "heading": "Fulfillment white-label",
                        "body": "Les commandes vont a Printful pour production et livraison avec votre branding. Retours selon la politique Printful.",
                    },
                    "cta": {"cta_primary_text": "Demander un devis"},
                },
                "de": {
                    "title": "So funktioniert Print Studio",
                    "nav_label": "Print Studio",
                    "meta_title": "So funktioniert Print Studio",
                    "meta_description": "White-label Ablauf fuer Print Studio.",
                    "hero": {
                        "heading": "So funktioniert Print Studio",
                        "subheading": "Wir betreiben den Store. Printful produziert und liefert.",
                        "cta_primary_text": "Druckprojekt starten",
                        "cta_secondary_text": "Support kontaktieren",
                    },
                    "main": {
                        "heading": "White-label Fulfillment",
                        "body": "Bestellungen gehen zu Printful fuer Produktion und Versand mit Ihrem Branding. Retouren folgen Printful Richtlinien.",
                    },
                    "cta": {"cta_primary_text": "Angebot anfordern"},
                },
                "es": {
                    "title": "Como funciona Print Studio",
                    "nav_label": "Print Studio",
                    "meta_title": "Como funciona Print Studio",
                    "meta_description": "Flujo white-label para Print Studio.",
                    "hero": {
                        "heading": "Como funciona Print Studio",
                        "subheading": "Gestionamos la tienda. Printful produce y envia.",
                        "cta_primary_text": "Iniciar proyecto print",
                        "cta_secondary_text": "Contactar soporte",
                    },
                    "main": {
                        "heading": "Fulfillment white-label",
                        "body": "Los pedidos van a Printful para produccion y envio con tu marca. Devoluciones segun politica Printful.",
                    },
                    "cta": {"cta_primary_text": "Pedir presupuesto"},
                },
                "pt": {
                    "title": "Como funciona o Print Studio",
                    "nav_label": "Print Studio",
                    "meta_title": "Como funciona o Print Studio",
                    "meta_description": "Fluxo white-label para Print Studio.",
                    "hero": {
                        "heading": "Como funciona o Print Studio",
                        "subheading": "Gerimos a loja. A Printful produz e envia.",
                        "cta_primary_text": "Iniciar projeto print",
                        "cta_secondary_text": "Contactar suporte",
                    },
                    "main": {
                        "heading": "Fulfillment white-label",
                        "body": "Encomendas vao para a Printful para producao e envio com a sua marca. Devolucoes seguem a politica Printful.",
                    },
                    "cta": {"cta_primary_text": "Pedir orcamento"},
                },
            },
            "print-lab-faq": {
                "en": {
                    "title": "Print Studio FAQ",
                    "nav_label": "Print Studio",
                    "meta_title": "Print Studio FAQ",
                    "meta_description": "FAQ for Print Studio, returns and fulfillment.",
                    "hero": {
                        "heading": "Print Studio FAQ",
                        "subheading": "Answers about printing, shipping, and returns.",
                        "cta_primary_text": "Contact support",
                        "cta_secondary_text": "View products",
                    },
                    "main": {
                        "heading": "Returns and defects",
                        "body": "Printful handles production and shipping. Returns and defects follow Printful policy.",
                    },
                    "cta": {"cta_primary_text": "Open support"},
                    "policy_notice": {
                        "heading": "Printful return policy",
                        "body": "Returns and defects are handled by Printful under their official policy.",
                        "cta_primary_text": "View Printful policy",
                        "cta_primary_url": "https://www.printful.com/policies/returns",
                    },
                },
                "nl": {
                    "title": "Print Studio FAQ",
                    "nav_label": "Print Studio",
                    "meta_title": "Print Studio FAQ",
                    "meta_description": "FAQ over Print Studio, retouren en fulfillment.",
                    "hero": {
                        "heading": "Print Studio FAQ",
                        "subheading": "Antwoorden over print, verzending en retouren.",
                        "cta_primary_text": "Contact support",
                        "cta_secondary_text": "Bekijk producten",
                    },
                    "main": {
                        "heading": "Retouren en defects",
                        "body": "Printful verzorgt productie en verzending. Retouren volgen Printful beleid.",
                    },
                    "cta": {"cta_primary_text": "Open support"},
                    "policy_notice": {
                        "heading": "Printful retourbeleid",
                        "body": "Retouren en defects worden door Printful afgehandeld volgens hun beleid.",
                        "cta_primary_text": "Bekijk Printful beleid",
                        "cta_primary_url": "https://www.printful.com/policies/returns",
                    },
                },
                "fr": {
                    "title": "Print Studio FAQ",
                    "nav_label": "Print Studio",
                    "meta_title": "Print Studio FAQ",
                    "meta_description": "FAQ Print Studio, retours et fulfillment.",
                    "hero": {
                        "heading": "Print Studio FAQ",
                        "subheading": "Reponses sur impression, livraison et retours.",
                        "cta_primary_text": "Contacter le support",
                        "cta_secondary_text": "Voir les produits",
                    },
                    "main": {
                        "heading": "Retours et defauts",
                        "body": "Printful gere production et livraison. Retours selon la politique Printful.",
                    },
                    "cta": {"cta_primary_text": "Ouvrir le support"},
                    "policy_notice": {
                        "heading": "Politique de retour Printful",
                        "body": "Les retours et defauts sont geres par Printful selon leur politique officielle.",
                        "cta_primary_text": "Voir la politique Printful",
                        "cta_primary_url": "https://www.printful.com/policies/returns",
                    },
                },
                "de": {
                    "title": "Print Studio FAQ",
                    "nav_label": "Print Studio",
                    "meta_title": "Print Studio FAQ",
                    "meta_description": "FAQ zu Print Studio, Retouren und Fulfillment.",
                    "hero": {
                        "heading": "Print Studio FAQ",
                        "subheading": "Antworten zu Druck, Versand und Retouren.",
                        "cta_primary_text": "Support kontaktieren",
                        "cta_secondary_text": "Produkte ansehen",
                    },
                    "main": {
                        "heading": "Retouren und Defekte",
                        "body": "Printful ubernimmt Produktion und Versand. Retouren folgen Printful Richtlinien.",
                    },
                    "cta": {"cta_primary_text": "Support offnen"},
                    "policy_notice": {
                        "heading": "Printful Retourenrichtlinie",
                        "body": "Retouren und Defekte werden von Printful nach deren offizieller Richtlinie bearbeitet.",
                        "cta_primary_text": "Printful Richtlinie ansehen",
                        "cta_primary_url": "https://www.printful.com/policies/returns",
                    },
                },
                "es": {
                    "title": "Print Studio FAQ",
                    "nav_label": "Print Studio",
                    "meta_title": "Print Studio FAQ",
                    "meta_description": "FAQ sobre Print Studio, devoluciones y fulfillment.",
                    "hero": {
                        "heading": "Print Studio FAQ",
                        "subheading": "Respuestas sobre impresion, envio y devoluciones.",
                        "cta_primary_text": "Contactar soporte",
                        "cta_secondary_text": "Ver productos",
                    },
                    "main": {
                        "heading": "Devoluciones y defectos",
                        "body": "Printful gestiona produccion y envio. Devoluciones segun politica Printful.",
                    },
                    "cta": {"cta_primary_text": "Abrir soporte"},
                    "policy_notice": {
                        "heading": "Politica de devoluciones Printful",
                        "body": "Devoluciones y defectos se gestionan con Printful segun su politica oficial.",
                        "cta_primary_text": "Ver politica Printful",
                        "cta_primary_url": "https://www.printful.com/policies/returns",
                    },
                },
                "pt": {
                    "title": "Print Studio FAQ",
                    "nav_label": "Print Studio",
                    "meta_title": "Print Studio FAQ",
                    "meta_description": "FAQ sobre Print Studio, devolucoes e fulfillment.",
                    "hero": {
                        "heading": "Print Studio FAQ",
                        "subheading": "Respostas sobre impressao, envio e devolucoes.",
                        "cta_primary_text": "Contactar suporte",
                        "cta_secondary_text": "Ver produtos",
                    },
                    "main": {
                        "heading": "Devolucoes e defeitos",
                        "body": "A Printful trata da producao e envio. Devolucoes seguem a politica Printful.",
                    },
                    "cta": {"cta_primary_text": "Abrir suporte"},
                    "policy_notice": {
                        "heading": "Politica de devolucoes Printful",
                        "body": "Devolucoes e defeitos sao tratados pela Printful segundo a politica oficial.",
                        "cta_primary_text": "Ver politica Printful",
                        "cta_primary_url": "https://www.printful.com/policies/returns",
                    },
                },
            },
            "billing": {
                "en": {
                    "title": "Billing",
                    "nav_label": "Billing",
                    "meta_title": "Billing",
                    "meta_description": "Manage your plan and invoices.",
                    "hero": {
                        "heading": "Billing overview",
                        "subheading": "Manage your plan, invoices, and payment details.",
                        "cta_primary_text": "Open billing portal",
                        "cta_secondary_text": "Contact support",
                    },
                    "main": {
                        "heading": "Payment details",
                        "body": "Update payment methods and download your invoices.",
                    },
                    "cta": {"cta_primary_text": "Go to portal"},
                },
                "nl": {
                    "title": "Facturatie",
                    "nav_label": "Facturatie",
                    "meta_title": "Facturatie",
                    "meta_description": "Beheer je abonnement en facturen.",
                    "hero": {
                        "heading": "Facturatieoverzicht",
                        "subheading": "Beheer je plan, facturen en betaalgegevens.",
                        "cta_primary_text": "Open betaalportaal",
                        "cta_secondary_text": "Contact support",
                    },
                    "main": {
                        "heading": "Betaalgegevens",
                        "body": "Werk betaalmethodes bij en download facturen.",
                    },
                    "cta": {"cta_primary_text": "Ga naar portaal"},
                },
                "fr": {
                    "title": "Facturation",
                    "nav_label": "Facturation",
                    "meta_title": "Facturation",
                    "meta_description": "Gerez votre plan et vos factures.",
                    "hero": {
                        "heading": "Apercu facturation",
                        "subheading": "Gerez votre plan, vos factures et vos paiements.",
                        "cta_primary_text": "Ouvrir le portail",
                        "cta_secondary_text": "Contacter le support",
                    },
                    "main": {
                        "heading": "Details de paiement",
                        "body": "Mettez a jour les paiements et telechargez vos factures.",
                    },
                    "cta": {"cta_primary_text": "Acceder au portail"},
                },
                "de": {
                    "title": "Abrechnung",
                    "nav_label": "Abrechnung",
                    "meta_title": "Abrechnung",
                    "meta_description": "Plan und Rechnungen verwalten.",
                    "hero": {
                        "heading": "Abrechnung",
                        "subheading": "Plan, Rechnungen und Zahlungsdaten verwalten.",
                        "cta_primary_text": "Portal oeffnen",
                        "cta_secondary_text": "Support kontaktieren",
                    },
                    "main": {
                        "heading": "Zahlungsdetails",
                        "body": "Zahlungsarten aktualisieren und Rechnungen herunterladen.",
                    },
                    "cta": {"cta_primary_text": "Zum Portal"},
                },
                "es": {
                    "title": "Facturacion",
                    "nav_label": "Facturacion",
                    "meta_title": "Facturacion",
                    "meta_description": "Gestiona tu plan y facturas.",
                    "hero": {
                        "heading": "Facturacion",
                        "subheading": "Gestiona tu plan, facturas y pagos.",
                        "cta_primary_text": "Abrir portal",
                        "cta_secondary_text": "Contactar soporte",
                    },
                    "main": {
                        "heading": "Detalles de pago",
                        "body": "Actualiza metodos de pago y descarga facturas.",
                    },
                    "cta": {"cta_primary_text": "Ir al portal"},
                },
                "pt": {
                    "title": "Faturacao",
                    "nav_label": "Faturacao",
                    "meta_title": "Faturacao",
                    "meta_description": "Gerir plano e faturas.",
                    "hero": {
                        "heading": "Faturacao",
                        "subheading": "Gerir plano, faturas e pagamentos.",
                        "cta_primary_text": "Abrir portal",
                        "cta_secondary_text": "Contactar suporte",
                    },
                    "main": {
                        "heading": "Detalhes de pagamento",
                        "body": "Atualize metodos de pagamento e descarregue faturas.",
                    },
                    "cta": {"cta_primary_text": "Ir ao portal"},
                },
            },
            "billing-checkout": {
                "en": {
                    "title": "Checkout",
                    "nav_label": "Checkout",
                    "meta_title": "Checkout",
                    "meta_description": "Complete your plan setup.",
                    "hero": {
                        "heading": "Checkout",
                        "subheading": "Complete your plan setup in a few steps.",
                        "cta_primary_text": "Continue",
                        "cta_secondary_text": "Back",
                    },
                    "main": {
                        "heading": "Secure checkout",
                        "body": "Your payment is processed securely and instantly.",
                    },
                    "cta": {"cta_primary_text": "Complete checkout"},
                },
                "nl": {
                    "title": "Afrekenen",
                    "nav_label": "Afrekenen",
                    "meta_title": "Afrekenen",
                    "meta_description": "Voltooi je planinstelling.",
                    "hero": {
                        "heading": "Afrekenen",
                        "subheading": "Rond je plan in enkele stappen af.",
                        "cta_primary_text": "Doorgaan",
                        "cta_secondary_text": "Terug",
                    },
                    "main": {
                        "heading": "Veilig afrekenen",
                        "body": "Je betaling wordt veilig en direct verwerkt.",
                    },
                    "cta": {"cta_primary_text": "Afrekenen"},
                },
                "fr": {
                    "title": "Paiement",
                    "nav_label": "Paiement",
                    "meta_title": "Paiement",
                    "meta_description": "Finalisez votre plan.",
                    "hero": {
                        "heading": "Paiement",
                        "subheading": "Finalisez votre plan en quelques etapes.",
                        "cta_primary_text": "Continuer",
                        "cta_secondary_text": "Retour",
                    },
                    "main": {
                        "heading": "Paiement securise",
                        "body": "Votre paiement est traite en toute securite.",
                    },
                    "cta": {"cta_primary_text": "Finaliser"},
                },
                "de": {
                    "title": "Checkout",
                    "nav_label": "Checkout",
                    "meta_title": "Checkout",
                    "meta_description": "Plan abschliessen.",
                    "hero": {
                        "heading": "Checkout",
                        "subheading": "Schliessen Sie Ihren Plan in wenigen Schritten ab.",
                        "cta_primary_text": "Weiter",
                        "cta_secondary_text": "Zurueck",
                    },
                    "main": {
                        "heading": "Sicher bezahlen",
                        "body": "Ihre Zahlung wird sicher verarbeitet.",
                    },
                    "cta": {"cta_primary_text": "Abschliessen"},
                },
                "es": {
                    "title": "Pago",
                    "nav_label": "Pago",
                    "meta_title": "Pago",
                    "meta_description": "Completa tu plan.",
                    "hero": {
                        "heading": "Pago",
                        "subheading": "Completa tu plan en unos pasos.",
                        "cta_primary_text": "Continuar",
                        "cta_secondary_text": "Volver",
                    },
                    "main": {
                        "heading": "Pago seguro",
                        "body": "Tu pago se procesa de forma segura.",
                    },
                    "cta": {"cta_primary_text": "Finalizar"},
                },
                "pt": {
                    "title": "Checkout",
                    "nav_label": "Checkout",
                    "meta_title": "Checkout",
                    "meta_description": "Conclua o seu plano.",
                    "hero": {
                        "heading": "Checkout",
                        "subheading": "Conclua o seu plano em poucos passos.",
                        "cta_primary_text": "Continuar",
                        "cta_secondary_text": "Voltar",
                    },
                    "main": {
                        "heading": "Pagamento seguro",
                        "body": "O seu pagamento e processado com seguranca.",
                    },
                    "cta": {"cta_primary_text": "Concluir"},
                },
            },
            "billing-success": {
                "en": {
                    "title": "Payment Success",
                    "nav_label": "Success",
                    "meta_title": "Payment Success",
                    "meta_description": "Your payment was successful.",
                    "hero": {
                        "heading": "Payment successful",
                        "subheading": "You're all set. We'll send you a confirmation email.",
                        "cta_primary_text": "Go to dashboard",
                        "cta_secondary_text": "Back to home",
                    },
                    "main": {
                        "heading": "What happens next",
                        "body": "We'll prepare your setup and notify you.",
                    },
                    "cta": {"cta_primary_text": "Return home"},
                },
                "nl": {
                    "title": "Betaling gelukt",
                    "nav_label": "Succes",
                    "meta_title": "Betaling gelukt",
                    "meta_description": "Je betaling is gelukt.",
                    "hero": {
                        "heading": "Betaling geslaagd",
                        "subheading": "Je bent klaar. We sturen een bevestiging per e-mail.",
                        "cta_primary_text": "Naar dashboard",
                        "cta_secondary_text": "Terug naar home",
                    },
                    "main": {
                        "heading": "Wat gebeurt er nu",
                        "body": "We bereiden je setup voor en laten het je weten.",
                    },
                    "cta": {"cta_primary_text": "Terug naar home"},
                },
                "fr": {
                    "title": "Paiement reussi",
                    "nav_label": "Succes",
                    "meta_title": "Paiement reussi",
                    "meta_description": "Votre paiement a reussi.",
                    "hero": {
                        "heading": "Paiement reussi",
                        "subheading": "Tout est ok. Un email de confirmation sera envoye.",
                        "cta_primary_text": "Aller au tableau",
                        "cta_secondary_text": "Retour accueil",
                    },
                    "main": {
                        "heading": "Et ensuite",
                        "body": "Nous preparons votre configuration et vous informons.",
                    },
                    "cta": {"cta_primary_text": "Retour accueil"},
                },
                "de": {
                    "title": "Zahlung erfolgreich",
                    "nav_label": "Erfolg",
                    "meta_title": "Zahlung erfolgreich",
                    "meta_description": "Ihre Zahlung war erfolgreich.",
                    "hero": {
                        "heading": "Zahlung erfolgreich",
                        "subheading": "Alles erledigt. Wir senden eine Bestaetigung per E-Mail.",
                        "cta_primary_text": "Zum Dashboard",
                        "cta_secondary_text": "Zur Startseite",
                    },
                    "main": {
                        "heading": "Wie es weitergeht",
                        "body": "Wir bereiten Ihr Setup vor und melden uns.",
                    },
                    "cta": {"cta_primary_text": "Zur Startseite"},
                },
                "es": {
                    "title": "Pago correcto",
                    "nav_label": "Exito",
                    "meta_title": "Pago correcto",
                    "meta_description": "Tu pago se realizo correctamente.",
                    "hero": {
                        "heading": "Pago correcto",
                        "subheading": "Todo listo. Te enviaremos un correo de confirmacion.",
                        "cta_primary_text": "Ir al panel",
                        "cta_secondary_text": "Volver al inicio",
                    },
                    "main": {
                        "heading": "Que sigue",
                        "body": "Preparamos tu configuracion y te avisamos.",
                    },
                    "cta": {"cta_primary_text": "Volver al inicio"},
                },
                "pt": {
                    "title": "Pagamento concluido",
                    "nav_label": "Sucesso",
                    "meta_title": "Pagamento concluido",
                    "meta_description": "O seu pagamento foi concluido.",
                    "hero": {
                        "heading": "Pagamento concluido",
                        "subheading": "Tudo pronto. Enviaremos um email de confirmacao.",
                        "cta_primary_text": "Ir ao painel",
                        "cta_secondary_text": "Voltar ao inicio",
                    },
                    "main": {
                        "heading": "Proximos passos",
                        "body": "Vamos preparar a sua configuracao e avisar.",
                    },
                    "cta": {"cta_primary_text": "Voltar ao inicio"},
                },
            },
            "billing-cancel": {
                "en": {
                    "title": "Checkout Canceled",
                    "nav_label": "Canceled",
                    "meta_title": "Checkout Canceled",
                    "meta_description": "Your checkout was canceled.",
                    "hero": {
                        "heading": "Checkout canceled",
                        "subheading": "No worries - your payment was not completed.",
                        "cta_primary_text": "Try again",
                        "cta_secondary_text": "Contact support",
                    },
                    "main": {
                        "heading": "Need help?",
                        "body": "We're here to help you finish your setup.",
                    },
                    "cta": {"cta_primary_text": "Contact support"},
                },
                "nl": {
                    "title": "Afrekenen geannuleerd",
                    "nav_label": "Geannuleerd",
                    "meta_title": "Afrekenen geannuleerd",
                    "meta_description": "Je afrekening is geannuleerd.",
                    "hero": {
                        "heading": "Afrekenen geannuleerd",
                        "subheading": "Geen zorgen - je betaling is niet afgerond.",
                        "cta_primary_text": "Probeer opnieuw",
                        "cta_secondary_text": "Contact support",
                    },
                    "main": {
                        "heading": "Hulp nodig?",
                        "body": "We helpen je graag met je setup.",
                    },
                    "cta": {"cta_primary_text": "Contact support"},
                },
                "fr": {
                    "title": "Paiement annule",
                    "nav_label": "Annule",
                    "meta_title": "Paiement annule",
                    "meta_description": "Votre paiement a ete annule.",
                    "hero": {
                        "heading": "Paiement annule",
                        "subheading": "Pas de souci - le paiement n'a pas ete complete.",
                        "cta_primary_text": "Reessayer",
                        "cta_secondary_text": "Contacter le support",
                    },
                    "main": {
                        "heading": "Besoin d'aide",
                        "body": "Nous sommes la pour finaliser votre configuration.",
                    },
                    "cta": {"cta_primary_text": "Contacter le support"},
                },
                "de": {
                    "title": "Checkout abgebrochen",
                    "nav_label": "Abgebrochen",
                    "meta_title": "Checkout abgebrochen",
                    "meta_description": "Ihr Checkout wurde abgebrochen.",
                    "hero": {
                        "heading": "Checkout abgebrochen",
                        "subheading": "Kein Problem - die Zahlung wurde nicht abgeschlossen.",
                        "cta_primary_text": "Erneut versuchen",
                        "cta_secondary_text": "Support kontaktieren",
                    },
                    "main": {
                        "heading": "Hilfe benoetigt",
                        "body": "Wir helfen Ihnen gerne beim Abschluss.",
                    },
                    "cta": {"cta_primary_text": "Support kontaktieren"},
                },
                "es": {
                    "title": "Pago cancelado",
                    "nav_label": "Cancelado",
                    "meta_title": "Pago cancelado",
                    "meta_description": "Tu pago fue cancelado.",
                    "hero": {
                        "heading": "Pago cancelado",
                        "subheading": "No pasa nada - el pago no se completo.",
                        "cta_primary_text": "Reintentar",
                        "cta_secondary_text": "Contactar soporte",
                    },
                    "main": {
                        "heading": "Necesitas ayuda",
                        "body": "Estamos aqui para ayudarte a finalizar.",
                    },
                    "cta": {"cta_primary_text": "Contactar soporte"},
                },
                "pt": {
                    "title": "Checkout cancelado",
                    "nav_label": "Cancelado",
                    "meta_title": "Checkout cancelado",
                    "meta_description": "O seu checkout foi cancelado.",
                    "hero": {
                        "heading": "Checkout cancelado",
                        "subheading": "Sem problema - o pagamento nao foi concluido.",
                        "cta_primary_text": "Tentar novamente",
                        "cta_secondary_text": "Contactar suporte",
                    },
                    "main": {
                        "heading": "Precisa de ajuda",
                        "body": "Estamos aqui para ajudar a finalizar.",
                    },
                    "cta": {"cta_primary_text": "Contactar suporte"},
                },
            },
            "billing-portal": {
                "en": {
                    "title": "Billing Portal",
                    "nav_label": "Billing Portal",
                    "meta_title": "Billing Portal",
                    "meta_description": "Manage subscriptions and payment methods.",
                    "hero": {
                        "heading": "Billing portal",
                        "subheading": "Update payment methods and manage subscriptions.",
                        "cta_primary_text": "Open portal",
                        "cta_secondary_text": "Contact support",
                    },
                    "main": {
                        "heading": "Manage your subscription",
                        "body": "Change plan, update billing info, and view invoices.",
                    },
                    "cta": {"cta_primary_text": "Open portal"},
                },
                "nl": {
                    "title": "Betaalportaal",
                    "nav_label": "Betaalportaal",
                    "meta_title": "Betaalportaal",
                    "meta_description": "Beheer abonnementen en betaalmethodes.",
                    "hero": {
                        "heading": "Betaalportaal",
                        "subheading": "Werk betaalmethodes bij en beheer abonnementen.",
                        "cta_primary_text": "Open portaal",
                        "cta_secondary_text": "Contact support",
                    },
                    "main": {
                        "heading": "Beheer je abonnement",
                        "body": "Plan wijzigen, betaalinfo bijwerken en facturen bekijken.",
                    },
                    "cta": {"cta_primary_text": "Open portaal"},
                },
                "fr": {
                    "title": "Portail de facturation",
                    "nav_label": "Portail",
                    "meta_title": "Portail de facturation",
                    "meta_description": "Gerez les abonnements et paiements.",
                    "hero": {
                        "heading": "Portail de facturation",
                        "subheading": "Mettez a jour les paiements et gerer les abonnements.",
                        "cta_primary_text": "Ouvrir le portail",
                        "cta_secondary_text": "Contacter le support",
                    },
                    "main": {
                        "heading": "Gerer votre abonnement",
                        "body": "Changer de plan, mettre a jour les infos et voir les factures.",
                    },
                    "cta": {"cta_primary_text": "Ouvrir le portail"},
                },
                "de": {
                    "title": "Abrechnungsportal",
                    "nav_label": "Portal",
                    "meta_title": "Abrechnungsportal",
                    "meta_description": "Abos und Zahlungsarten verwalten.",
                    "hero": {
                        "heading": "Abrechnungsportal",
                        "subheading": "Zahlungsarten aktualisieren und Abos verwalten.",
                        "cta_primary_text": "Portal oeffnen",
                        "cta_secondary_text": "Support kontaktieren",
                    },
                    "main": {
                        "heading": "Abo verwalten",
                        "body": "Plan wechseln, Daten aktualisieren und Rechnungen ansehen.",
                    },
                    "cta": {"cta_primary_text": "Portal oeffnen"},
                },
                "es": {
                    "title": "Portal de facturacion",
                    "nav_label": "Portal",
                    "meta_title": "Portal de facturacion",
                    "meta_description": "Gestiona suscripciones y pagos.",
                    "hero": {
                        "heading": "Portal de facturacion",
                        "subheading": "Actualiza pagos y gestiona suscripciones.",
                        "cta_primary_text": "Abrir portal",
                        "cta_secondary_text": "Contactar soporte",
                    },
                    "main": {
                        "heading": "Gestiona tu suscripcion",
                        "body": "Cambiar plan, actualizar datos y ver facturas.",
                    },
                    "cta": {"cta_primary_text": "Abrir portal"},
                },
                "pt": {
                    "title": "Portal de faturacao",
                    "nav_label": "Portal",
                    "meta_title": "Portal de faturacao",
                    "meta_description": "Gerir subscricoes e pagamentos.",
                    "hero": {
                        "heading": "Portal de faturacao",
                        "subheading": "Atualize pagamentos e gerencie subscricoes.",
                        "cta_primary_text": "Abrir portal",
                        "cta_secondary_text": "Contactar suporte",
                    },
                    "main": {
                        "heading": "Gerir a sua subscricao",
                        "body": "Alterar plano, atualizar dados e ver faturas.",
                    },
                    "cta": {"cta_primary_text": "Abrir portal"},
                },
            },
            "printful": {
                "en": {
                    "title": "Printful",
                    "nav_label": "Printful",
                    "meta_title": "Printful",
                    "meta_description": "Connect Printful for on-demand fulfillment.",
                    "hero": {
                        "heading": "Printful integration",
                        "subheading": "Connect Printful and automate fulfillment.",
                        "cta_primary_text": "Connect Printful",
                        "cta_secondary_text": "View products",
                    },
                    "main": {
                        "heading": "Automated fulfillment",
                        "body": "Sync products and track orders in one place.",
                    },
                    "cta": {"cta_primary_text": "Get started"},
                },
                "nl": {
                    "title": "Printful",
                    "nav_label": "Printful",
                    "meta_title": "Printful",
                    "meta_description": "Koppel Printful voor on-demand fulfilment.",
                    "hero": {
                        "heading": "Printful-integratie",
                        "subheading": "Koppel Printful en automatiseer fulfilment.",
                        "cta_primary_text": "Koppel Printful",
                        "cta_secondary_text": "Bekijk producten",
                    },
                    "main": {
                        "heading": "Geautomatiseerde fulfilment",
                        "body": "Synchroniseer producten en volg bestellingen.",
                    },
                    "cta": {"cta_primary_text": "Start"},
                },
                "fr": {
                    "title": "Printful",
                    "nav_label": "Printful",
                    "meta_title": "Printful",
                    "meta_description": "Connectez Printful pour la production a la demande.",
                    "hero": {
                        "heading": "Integration Printful",
                        "subheading": "Connectez Printful et automatisez la production.",
                        "cta_primary_text": "Connecter Printful",
                        "cta_secondary_text": "Voir les produits",
                    },
                    "main": {
                        "heading": "Production automatisee",
                        "body": "Synchronisez les produits et suivez les commandes.",
                    },
                    "cta": {"cta_primary_text": "Commencer"},
                },
                "de": {
                    "title": "Printful",
                    "nav_label": "Printful",
                    "meta_title": "Printful",
                    "meta_description": "Printful fuer On-Demand-Fulfillment verbinden.",
                    "hero": {
                        "heading": "Printful-Integration",
                        "subheading": "Printful verbinden und Fulfillment automatisieren.",
                        "cta_primary_text": "Printful verbinden",
                        "cta_secondary_text": "Produkte ansehen",
                    },
                    "main": {
                        "heading": "Automatisiertes Fulfillment",
                        "body": "Produkte synchronisieren und Bestellungen verfolgen.",
                    },
                    "cta": {"cta_primary_text": "Loslegen"},
                },
                "es": {
                    "title": "Printful",
                    "nav_label": "Printful",
                    "meta_title": "Printful",
                    "meta_description": "Conecta Printful para fulfillment bajo demanda.",
                    "hero": {
                        "heading": "Integracion Printful",
                        "subheading": "Conecta Printful y automatiza el fulfillment.",
                        "cta_primary_text": "Conectar Printful",
                        "cta_secondary_text": "Ver productos",
                    },
                    "main": {
                        "heading": "Fulfillment automatizado",
                        "body": "Sincroniza productos y sigue pedidos en un solo lugar.",
                    },
                    "cta": {"cta_primary_text": "Empezar"},
                },
                "pt": {
                    "title": "Printful",
                    "nav_label": "Printful",
                    "meta_title": "Printful",
                    "meta_description": "Ligue o Printful para fulfillment on-demand.",
                    "hero": {
                        "heading": "Integracao Printful",
                        "subheading": "Ligue o Printful e automatize o fulfillment.",
                        "cta_primary_text": "Ligar Printful",
                        "cta_secondary_text": "Ver produtos",
                    },
                    "main": {
                        "heading": "Fulfillment automatizado",
                        "body": "Sincronize produtos e acompanhe encomendas.",
                    },
                    "cta": {"cta_primary_text": "Comecar"},
                },
            },
            "printful-products": {
                "en": {
                    "title": "Printful Products",
                    "nav_label": "Printful Products",
                    "meta_title": "Printful Products",
                    "meta_description": "Manage your Printful catalog.",
                    "hero": {
                        "heading": "Printful products",
                        "subheading": "Manage and sync your Printful catalog.",
                        "cta_primary_text": "Sync products",
                        "cta_secondary_text": "View orders",
                    },
                    "main": {
                        "heading": "Your product list",
                        "body": "Import, update, and publish products quickly.",
                    },
                    "cta": {"cta_primary_text": "Sync now"},
                },
                "nl": {
                    "title": "Printful-producten",
                    "nav_label": "Printful-producten",
                    "meta_title": "Printful-producten",
                    "meta_description": "Beheer je Printful-catalogus.",
                    "hero": {
                        "heading": "Printful-producten",
                        "subheading": "Beheer en synchroniseer je catalogus.",
                        "cta_primary_text": "Producten syncen",
                        "cta_secondary_text": "Bekijk orders",
                    },
                    "main": {
                        "heading": "Je productlijst",
                        "body": "Importeer, update en publiceer producten snel.",
                    },
                    "cta": {"cta_primary_text": "Nu syncen"},
                },
                "fr": {
                    "title": "Produits Printful",
                    "nav_label": "Produits Printful",
                    "meta_title": "Produits Printful",
                    "meta_description": "Gerez le catalogue Printful.",
                    "hero": {
                        "heading": "Produits Printful",
                        "subheading": "Gerez et synchronisez votre catalogue.",
                        "cta_primary_text": "Synchroniser",
                        "cta_secondary_text": "Voir les commandes",
                    },
                    "main": {
                        "heading": "Votre liste de produits",
                        "body": "Importez, mettez a jour et publiez rapidement.",
                    },
                    "cta": {"cta_primary_text": "Synchroniser"},
                },
                "de": {
                    "title": "Printful-Produkte",
                    "nav_label": "Printful-Produkte",
                    "meta_title": "Printful-Produkte",
                    "meta_description": "Printful-Katalog verwalten.",
                    "hero": {
                        "heading": "Printful-Produkte",
                        "subheading": "Printful-Katalog verwalten und synchronisieren.",
                        "cta_primary_text": "Produkte syncen",
                        "cta_secondary_text": "Bestellungen ansehen",
                    },
                    "main": {
                        "heading": "Ihre Produktliste",
                        "body": "Importieren, aktualisieren und veroeffentlichen.",
                    },
                    "cta": {"cta_primary_text": "Jetzt syncen"},
                },
                "es": {
                    "title": "Productos Printful",
                    "nav_label": "Productos Printful",
                    "meta_title": "Productos Printful",
                    "meta_description": "Gestiona el catalogo Printful.",
                    "hero": {
                        "heading": "Productos Printful",
                        "subheading": "Gestiona y sincroniza tu catalogo.",
                        "cta_primary_text": "Sincronizar",
                        "cta_secondary_text": "Ver pedidos",
                    },
                    "main": {
                        "heading": "Tu lista de productos",
                        "body": "Importa, actualiza y publica rapidamente.",
                    },
                    "cta": {"cta_primary_text": "Sincronizar ahora"},
                },
                "pt": {
                    "title": "Produtos Printful",
                    "nav_label": "Produtos Printful",
                    "meta_title": "Produtos Printful",
                    "meta_description": "Gerir o catalogo Printful.",
                    "hero": {
                        "heading": "Produtos Printful",
                        "subheading": "Gerir e sincronizar o catalogo.",
                        "cta_primary_text": "Sincronizar",
                        "cta_secondary_text": "Ver encomendas",
                    },
                    "main": {
                        "heading": "A sua lista de produtos",
                        "body": "Importe, atualize e publique rapidamente.",
                    },
                    "cta": {"cta_primary_text": "Sincronizar agora"},
                },
            },
            "printful-orders": {
                "en": {
                    "title": "Printful Orders",
                    "nav_label": "Printful Orders",
                    "meta_title": "Printful Orders",
                    "meta_description": "Track Printful fulfillment and shipments.",
                    "hero": {
                        "heading": "Printful orders",
                        "subheading": "Track fulfillment status and shipments in one place.",
                        "cta_primary_text": "View orders",
                        "cta_secondary_text": "Contact support",
                    },
                    "main": {
                        "heading": "Order status",
                        "body": "Monitor production, shipping, and delivery updates.",
                    },
                    "cta": {"cta_primary_text": "Open orders"},
                },
                "nl": {
                    "title": "Printful-orders",
                    "nav_label": "Printful-orders",
                    "meta_title": "Printful-orders",
                    "meta_description": "Volg Printful-fulfilment en verzendingen.",
                    "hero": {
                        "heading": "Printful-orders",
                        "subheading": "Volg fulfilmentstatus en zendingen op een plek.",
                        "cta_primary_text": "Bekijk orders",
                        "cta_secondary_text": "Contact support",
                    },
                    "main": {
                        "heading": "Orderstatus",
                        "body": "Volg productie, verzending en levering.",
                    },
                    "cta": {"cta_primary_text": "Open orders"},
                },
                "fr": {
                    "title": "Commandes Printful",
                    "nav_label": "Commandes Printful",
                    "meta_title": "Commandes Printful",
                    "meta_description": "Suivez la production et les expeditions Printful.",
                    "hero": {
                        "heading": "Commandes Printful",
                        "subheading": "Suivez la production et les expeditions.",
                        "cta_primary_text": "Voir les commandes",
                        "cta_secondary_text": "Contacter le support",
                    },
                    "main": {
                        "heading": "Statut des commandes",
                        "body": "Suivez production, expedition et livraison.",
                    },
                    "cta": {"cta_primary_text": "Ouvrir les commandes"},
                },
                "de": {
                    "title": "Printful-Bestellungen",
                    "nav_label": "Printful-Bestellungen",
                    "meta_title": "Printful-Bestellungen",
                    "meta_description": "Printful-Fulfillment und Versand verfolgen.",
                    "hero": {
                        "heading": "Printful-Bestellungen",
                        "subheading": "Fulfillment und Versandstatus verfolgen.",
                        "cta_primary_text": "Bestellungen ansehen",
                        "cta_secondary_text": "Support kontaktieren",
                    },
                    "main": {
                        "heading": "Bestellstatus",
                        "body": "Produktion, Versand und Lieferung im Blick.",
                    },
                    "cta": {"cta_primary_text": "Bestellungen oeffnen"},
                },
                "es": {
                    "title": "Pedidos Printful",
                    "nav_label": "Pedidos Printful",
                    "meta_title": "Pedidos Printful",
                    "meta_description": "Sigue la produccion y envios Printful.",
                    "hero": {
                        "heading": "Pedidos Printful",
                        "subheading": "Sigue el estado de produccion y envio.",
                        "cta_primary_text": "Ver pedidos",
                        "cta_secondary_text": "Contactar soporte",
                    },
                    "main": {
                        "heading": "Estado del pedido",
                        "body": "Controla produccion, envio y entrega.",
                    },
                    "cta": {"cta_primary_text": "Abrir pedidos"},
                },
                "pt": {
                    "title": "Encomendas Printful",
                    "nav_label": "Encomendas Printful",
                    "meta_title": "Encomendas Printful",
                    "meta_description": "Acompanhe o fulfillment e envios Printful.",
                    "hero": {
                        "heading": "Encomendas Printful",
                        "subheading": "Acompanhe o estado de fulfillment e envios.",
                        "cta_primary_text": "Ver encomendas",
                        "cta_secondary_text": "Contactar suporte",
                    },
                    "main": {
                        "heading": "Estado das encomendas",
                        "body": "Acompanhe producao, envio e entrega.",
                    },
                    "cta": {"cta_primary_text": "Abrir encomendas"},
                },
            },
        }

        pos_affiliate_translations = {
            "en": {
                "affiliate_disclosure": {
                    "body": "Some links may be affiliate links. This does not change the price you pay.",
                },
                "affiliate_blocks": [
                    {
                        "heading": "Lightspeed POS",
                        "subheading": "Retail and inventory",
                        "body": "Tools for stock, staff, and customers.",
                        "cta_primary_text": "View pricing",
                        "cta_primary_url": "https://example.com/pos/lightspeed",
                        "cta_secondary_text": "See demo",
                        "cta_secondary_url": "https://example.com/pos/lightspeed/demo",
                    },
                    {
                        "heading": "SumUp POS",
                        "subheading": "Simple card payments",
                        "body": "Quick setup for small teams and cafes.",
                        "cta_primary_text": "View pricing",
                        "cta_primary_url": "https://example.com/pos/sumup",
                        "cta_secondary_text": "Learn more",
                        "cta_secondary_url": "https://example.com/pos/sumup/details",
                    },
                    {
                        "heading": "Square POS",
                        "subheading": "Simple for services",
                        "body": "Appointments and receipts in one place.",
                        "cta_primary_text": "View pricing",
                        "cta_primary_url": "https://example.com/pos/square",
                        "cta_secondary_text": "Learn more",
                        "cta_secondary_url": "https://example.com/pos/square/details",
                    },
                ],
            },
            "nl": {
                "affiliate_disclosure": {
                    "body": "Sommige links zijn affiliate links. Dit verandert de prijs niet.",
                },
                "affiliate_blocks": [
                    {
                        "heading": "Lightspeed POS",
                        "subheading": "Retail en voorraad",
                        "body": "Tools voor voorraad, team en klanten.",
                        "cta_primary_text": "Bekijk prijzen",
                        "cta_primary_url": "https://example.com/pos/lightspeed",
                        "cta_secondary_text": "Bekijk demo",
                        "cta_secondary_url": "https://example.com/pos/lightspeed/demo",
                    },
                    {
                        "heading": "SumUp POS",
                        "subheading": "Eenvoudige kaartbetalingen",
                        "body": "Snelle setup voor kleine teams en cafes.",
                        "cta_primary_text": "Bekijk prijzen",
                        "cta_primary_url": "https://example.com/pos/sumup",
                        "cta_secondary_text": "Meer info",
                        "cta_secondary_url": "https://example.com/pos/sumup/details",
                    },
                    {
                        "heading": "Square POS",
                        "subheading": "Handig voor diensten",
                        "body": "Afspraken en bonnen op een plek.",
                        "cta_primary_text": "Bekijk prijzen",
                        "cta_primary_url": "https://example.com/pos/square",
                        "cta_secondary_text": "Meer info",
                        "cta_secondary_url": "https://example.com/pos/square/details",
                    },
                ],
            },
            "fr": {
                "affiliate_disclosure": {
                    "body": "Certains liens peuvent etre des liens d affiliation. Le prix ne change pas.",
                },
                "affiliate_blocks": [
                    {
                        "heading": "Lightspeed POS",
                        "subheading": "Retail et stock",
                        "body": "Outils pour stock, equipe et clients.",
                        "cta_primary_text": "Voir les prix",
                        "cta_primary_url": "https://example.com/pos/lightspeed",
                        "cta_secondary_text": "Voir la demo",
                        "cta_secondary_url": "https://example.com/pos/lightspeed/demo",
                    },
                    {
                        "heading": "SumUp POS",
                        "subheading": "Paiements simples",
                        "body": "Mise en place rapide pour petites equipes.",
                        "cta_primary_text": "Voir les prix",
                        "cta_primary_url": "https://example.com/pos/sumup",
                        "cta_secondary_text": "En savoir plus",
                        "cta_secondary_url": "https://example.com/pos/sumup/details",
                    },
                    {
                        "heading": "Square POS",
                        "subheading": "Pratique pour services",
                        "body": "Rendez-vous et reçus au meme endroit.",
                        "cta_primary_text": "Voir les prix",
                        "cta_primary_url": "https://example.com/pos/square",
                        "cta_secondary_text": "En savoir plus",
                        "cta_secondary_url": "https://example.com/pos/square/details",
                    },
                ],
            },
            "de": {
                "affiliate_disclosure": {
                    "body": "Einige Links sind Affiliate Links. Der Preis bleibt gleich.",
                },
                "affiliate_blocks": [
                    {
                        "heading": "Lightspeed POS",
                        "subheading": "Retail und Bestand",
                        "body": "Tools fuer Bestand, Team und Kunden.",
                        "cta_primary_text": "Preise ansehen",
                        "cta_primary_url": "https://example.com/pos/lightspeed",
                        "cta_secondary_text": "Demo ansehen",
                        "cta_secondary_url": "https://example.com/pos/lightspeed/demo",
                    },
                    {
                        "heading": "SumUp POS",
                        "subheading": "Einfache Kartenzahlung",
                        "body": "Schneller Start fuer kleine Teams.",
                        "cta_primary_text": "Preise ansehen",
                        "cta_primary_url": "https://example.com/pos/sumup",
                        "cta_secondary_text": "Mehr erfahren",
                        "cta_secondary_url": "https://example.com/pos/sumup/details",
                    },
                    {
                        "heading": "Square POS",
                        "subheading": "Gut fuer Services",
                        "body": "Termine und Belege an einem Ort.",
                        "cta_primary_text": "Preise ansehen",
                        "cta_primary_url": "https://example.com/pos/square",
                        "cta_secondary_text": "Mehr erfahren",
                        "cta_secondary_url": "https://example.com/pos/square/details",
                    },
                ],
            },
            "es": {
                "affiliate_disclosure": {
                    "body": "Algunos enlaces pueden ser de afiliados. El precio no cambia.",
                },
                "affiliate_blocks": [
                    {
                        "heading": "Lightspeed POS",
                        "subheading": "Retail e inventario",
                        "body": "Herramientas para stock, equipo y clientes.",
                        "cta_primary_text": "Ver precios",
                        "cta_primary_url": "https://example.com/pos/lightspeed",
                        "cta_secondary_text": "Ver demo",
                        "cta_secondary_url": "https://example.com/pos/lightspeed/demo",
                    },
                    {
                        "heading": "SumUp POS",
                        "subheading": "Pagos simples",
                        "body": "Inicio rapido para equipos pequenos.",
                        "cta_primary_text": "Ver precios",
                        "cta_primary_url": "https://example.com/pos/sumup",
                        "cta_secondary_text": "Mas info",
                        "cta_secondary_url": "https://example.com/pos/sumup/details",
                    },
                    {
                        "heading": "Square POS",
                        "subheading": "Ideal para servicios",
                        "body": "Citas y recibos en un solo lugar.",
                        "cta_primary_text": "Ver precios",
                        "cta_primary_url": "https://example.com/pos/square",
                        "cta_secondary_text": "Mas info",
                        "cta_secondary_url": "https://example.com/pos/square/details",
                    },
                ],
            },
            "pt": {
                "affiliate_disclosure": {
                    "body": "Alguns links podem ser de afiliados. O preco nao muda.",
                },
                "affiliate_blocks": [
                    {
                        "heading": "Lightspeed POS",
                        "subheading": "Retalho e stock",
                        "body": "Ferramentas para stock, equipa e clientes.",
                        "cta_primary_text": "Ver precos",
                        "cta_primary_url": "https://example.com/pos/lightspeed",
                        "cta_secondary_text": "Ver demo",
                        "cta_secondary_url": "https://example.com/pos/lightspeed/demo",
                    },
                    {
                        "heading": "SumUp POS",
                        "subheading": "Pagamentos simples",
                        "body": "Arranque rapido para equipas pequenas.",
                        "cta_primary_text": "Ver precos",
                        "cta_primary_url": "https://example.com/pos/sumup",
                        "cta_secondary_text": "Mais info",
                        "cta_secondary_url": "https://example.com/pos/sumup/details",
                    },
                    {
                        "heading": "Square POS",
                        "subheading": "Bom para servicos",
                        "body": "Marcacoes e recibos num so lugar.",
                        "cta_primary_text": "Ver precos",
                        "cta_primary_url": "https://example.com/pos/square",
                        "cta_secondary_text": "Mais info",
                        "cta_secondary_url": "https://example.com/pos/square/details",
                    },
                ],
            },
        }

        for lang in languages:
            page_translations["pos-systems"][lang].update(pos_affiliate_translations[lang])


        pos_pages_translations = {
            "pos-systems-retail": {
                "en": {
                    "title": "Retail POS",
                    "nav_label": "Retail POS",
                    "meta_title": "Retail POS",
                    "meta_description": "Retail POS options for shops and boutiques.",
                    "hero": {
                        "heading": "Retail POS",
                        "subheading": "For shops and boutiques. Fast checkout and simple inventory.",
                        "cta_primary_text": "View partners",
                        "cta_secondary_text": "Get a recommendation",
                    },
                    "main": {
                        "heading": "What to look for",
                        "body": "Barcode support, inventory basics, staff roles, and simple reports.",
                    },
                    "cta": {
                        "heading": "Want a shortlist?",
                        "body": "Tell us your shop type and we will suggest options.",
                        "cta_primary_text": "Get a recommendation",
                        "cta_primary_url": "/help-center/",
                    },
                    "affiliate_disclosure": {
                        "body": "Some links may be affiliate links. This does not change the price you pay.",
                    },
                    **pos_affiliate_translations["en"],
                },
                "nl": {
                    "title": "Retail POS",
                    "nav_label": "Retail POS",
                    "meta_title": "Retail POS",
                    "meta_description": "POS opties voor winkels en boutiques.",
                    "hero": {
                        "heading": "Retail POS",
                        "subheading": "Voor winkels en boutiques. Snelle checkout en eenvoudige voorraad.",
                        "cta_primary_text": "Bekijk partners",
                        "cta_secondary_text": "Krijg advies",
                    },
                    "main": {
                        "heading": "Waarop letten",
                        "body": "Barcode ondersteuning, eenvoudige voorraad, teamrollen en rapporten.",
                    },
                    "cta": {
                        "heading": "Korte lijst nodig?",
                        "body": "Vertel je winkeltype en we geven opties.",
                        "cta_primary_text": "Krijg advies",
                        "cta_primary_url": "/help-center/",
                    },
                    "affiliate_disclosure": {
                        "body": "Sommige links kunnen affiliate links zijn. Dit verandert de prijs niet.",
                    },
                    **pos_affiliate_translations["nl"],
                },
                "fr": {
                    "title": "POS retail",
                    "nav_label": "POS retail",
                    "meta_title": "POS retail",
                    "meta_description": "Options POS pour boutiques et commerces.",
                    "hero": {
                        "heading": "POS retail",
                        "subheading": "Pour boutiques et commerces. Encaissement rapide et stock simple.",
                        "cta_primary_text": "Voir les partenaires",
                        "cta_secondary_text": "Demander un conseil",
                    },
                    "main": {
                        "heading": "Points importants",
                        "body": "Codes barres, stock de base, roles equipe et rapports simples.",
                    },
                    "cta": {
                        "heading": "Besoin d'une selection?",
                        "body": "Dites votre type de boutique et nous proposerons des options.",
                        "cta_primary_text": "Demander un conseil",
                        "cta_primary_url": "/help-center/",
                    },
                    "affiliate_disclosure": {
                        "body": "Certains liens peuvent etre des liens d'affiliation. Cela ne change pas le prix.",
                    },
                    **pos_affiliate_translations["fr"],
                },
                "de": {
                    "title": "Retail POS",
                    "nav_label": "Retail POS",
                    "meta_title": "Retail POS",
                    "meta_description": "Retail POS Optionen fuer Shops und Boutiquen.",
                    "hero": {
                        "heading": "Retail POS",
                        "subheading": "Fuer Shops und Boutiquen. Schneller Checkout und einfache Warenwirtschaft.",
                        "cta_primary_text": "Partner ansehen",
                        "cta_secondary_text": "Empfehlung erhalten",
                    },
                    "main": {
                        "heading": "Worauf achten",
                        "body": "Barcode, einfacher Bestand, Rollen fuer Teams und klare Berichte.",
                    },
                    "cta": {
                        "heading": "Kurzliste gesucht?",
                        "body": "Nennen Sie Ihren Shop und wir schlagen Optionen vor.",
                        "cta_primary_text": "Empfehlung erhalten",
                        "cta_primary_url": "/help-center/",
                    },
                    "affiliate_disclosure": {
                        "body": "Einige Links koennen Affiliate-Links sein. Das aendert den Preis nicht.",
                    },
                    **pos_affiliate_translations["de"],
                },
                "es": {
                    "title": "POS retail",
                    "nav_label": "POS retail",
                    "meta_title": "POS retail",
                    "meta_description": "Opciones POS para tiendas y boutiques.",
                    "hero": {
                        "heading": "POS retail",
                        "subheading": "Para tiendas y boutiques. Cobro rapido e inventario simple.",
                        "cta_primary_text": "Ver partners",
                        "cta_secondary_text": "Pedir recomendacion",
                    },
                    "main": {
                        "heading": "En que fijarse",
                        "body": "Codigos de barras, inventario basico, roles y reportes simples.",
                    },
                    "cta": {
                        "heading": "Necesitas una lista corta?",
                        "body": "Dinos tu tipo de tienda y sugerimos opciones.",
                        "cta_primary_text": "Pedir recomendacion",
                        "cta_primary_url": "/help-center/",
                    },
                    "affiliate_disclosure": {
                        "body": "Algunos enlaces pueden ser de afiliados. No cambia el precio.",
                    },
                    **pos_affiliate_translations["es"],
                },
                "pt": {
                    "title": "POS retalho",
                    "nav_label": "POS retalho",
                    "meta_title": "POS retalho",
                    "meta_description": "Opcoes POS para lojas e boutiques.",
                    "hero": {
                        "heading": "POS retalho",
                        "subheading": "Para lojas e boutiques. Checkout rapido e stock simples.",
                        "cta_primary_text": "Ver parceiros",
                        "cta_secondary_text": "Pedir recomendacao",
                    },
                    "main": {
                        "heading": "O que procurar",
                        "body": "Codigos de barras, stock basico, perfis de equipa e relatorios simples.",
                    },
                    "cta": {
                        "heading": "Precisa de uma lista curta?",
                        "body": "Diga o seu tipo de loja e sugerimos opcoes.",
                        "cta_primary_text": "Pedir recomendacao",
                        "cta_primary_url": "/help-center/",
                    },
                    "affiliate_disclosure": {
                        "body": "Alguns links podem ser de afiliados. Isso nao altera o preco.",
                    },
                    **pos_affiliate_translations["pt"],
                },
            },
            "pos-systems-hospitality": {
                "en": {
                    "title": "Hospitality POS",
                    "nav_label": "Hospitality POS",
                    "meta_title": "Hospitality POS",
                    "meta_description": "POS options for cafes, bars, and restaurants.",
                    "hero": {
                        "heading": "Hospitality POS",
                        "subheading": "For cafes, bars, and restaurants. Tables, tips, and quick checkout.",
                        "cta_primary_text": "View partners",
                        "cta_secondary_text": "Get a recommendation",
                    },
                    "main": {
                        "heading": "Designed for busy floors",
                        "body": "Look for table management, split bills, and kitchen tickets.",
                    },
                    "cta": {
                        "heading": "Need a shortlist?",
                        "body": "Tell us your venue type and we will suggest options.",
                        "cta_primary_text": "Get a recommendation",
                        "cta_primary_url": "/help-center/",
                    },
                    "affiliate_disclosure": {
                        "body": "Some links may be affiliate links. This does not change the price you pay.",
                    },
                    **pos_affiliate_translations["en"],
                },
                "nl": {
                    "title": "Horeca POS",
                    "nav_label": "Horeca POS",
                    "meta_title": "Horeca POS",
                    "meta_description": "POS opties voor cafes, bars en restaurants.",
                    "hero": {
                        "heading": "Horeca POS",
                        "subheading": "Voor cafes, bars en restaurants. Tafels, fooien en snelle checkout.",
                        "cta_primary_text": "Bekijk partners",
                        "cta_secondary_text": "Krijg advies",
                    },
                    "main": {
                        "heading": "Voor drukke zaken",
                        "body": "Kijk naar tafelbeheer, split bills en keukenbonnen.",
                    },
                    "cta": {
                        "heading": "Korte lijst nodig?",
                        "body": "Vertel je type zaak en we geven opties.",
                        "cta_primary_text": "Krijg advies",
                        "cta_primary_url": "/help-center/",
                    },
                    "affiliate_disclosure": {
                        "body": "Sommige links kunnen affiliate links zijn. Dit verandert de prijs niet.",
                    },
                    **pos_affiliate_translations["nl"],
                },
                "fr": {
                    "title": "POS restauration",
                    "nav_label": "POS restauration",
                    "meta_title": "POS restauration",
                    "meta_description": "Options POS pour cafes, bars et restaurants.",
                    "hero": {
                        "heading": "POS restauration",
                        "subheading": "Pour cafes, bars et restaurants. Tables, pourboires et encaissement rapide.",
                        "cta_primary_text": "Voir les partenaires",
                        "cta_secondary_text": "Demander un conseil",
                    },
                    "main": {
                        "heading": "Pour le service",
                        "body": "Gestion des tables, additions partagees et tickets cuisine.",
                    },
                    "cta": {
                        "heading": "Besoin d'une selection?",
                        "body": "Dites votre type d'etablissement et nous proposerons des options.",
                        "cta_primary_text": "Demander un conseil",
                        "cta_primary_url": "/help-center/",
                    },
                    "affiliate_disclosure": {
                        "body": "Certains liens peuvent etre des liens d'affiliation. Cela ne change pas le prix.",
                    },
                    **pos_affiliate_translations["fr"],
                },
                "de": {
                    "title": "Gastro POS",
                    "nav_label": "Gastro POS",
                    "meta_title": "Gastro POS",
                    "meta_description": "POS Optionen fuer Cafes, Bars und Restaurants.",
                    "hero": {
                        "heading": "Gastro POS",
                        "subheading": "Fuer Cafes, Bars und Restaurants. Tische, Trinkgeld und schneller Checkout.",
                        "cta_primary_text": "Partner ansehen",
                        "cta_secondary_text": "Empfehlung erhalten",
                    },
                    "main": {
                        "heading": "Fuer den Service",
                        "body": "Tischverwaltung, geteilte Rechnungen und Kuechentickets.",
                    },
                    "cta": {
                        "heading": "Kurzliste gesucht?",
                        "body": "Nennen Sie Ihren Betrieb und wir schlagen Optionen vor.",
                        "cta_primary_text": "Empfehlung erhalten",
                        "cta_primary_url": "/help-center/",
                    },
                    "affiliate_disclosure": {
                        "body": "Einige Links koennen Affiliate-Links sein. Das aendert den Preis nicht.",
                    },
                    **pos_affiliate_translations["de"],
                },
                "es": {
                    "title": "POS hosteleria",
                    "nav_label": "POS hosteleria",
                    "meta_title": "POS hosteleria",
                    "meta_description": "Opciones POS para cafes, bares y restaurantes.",
                    "hero": {
                        "heading": "POS hosteleria",
                        "subheading": "Para cafes, bares y restaurantes. Mesas, propinas y cobro rapido.",
                        "cta_primary_text": "Ver partners",
                        "cta_secondary_text": "Pedir recomendacion",
                    },
                    "main": {
                        "heading": "Pensado para sala",
                        "body": "Mesas, cuentas divididas y tickets de cocina.",
                    },
                    "cta": {
                        "heading": "Necesitas una lista corta?",
                        "body": "Dinos tu tipo de local y sugerimos opciones.",
                        "cta_primary_text": "Pedir recomendacion",
                        "cta_primary_url": "/help-center/",
                    },
                    "affiliate_disclosure": {
                        "body": "Algunos enlaces pueden ser de afiliados. No cambia el precio.",
                    },
                    **pos_affiliate_translations["es"],
                },
                "pt": {
                    "title": "POS hotelaria",
                    "nav_label": "POS hotelaria",
                    "meta_title": "POS hotelaria",
                    "meta_description": "Opcoes POS para cafes, bares e restaurantes.",
                    "hero": {
                        "heading": "POS hotelaria",
                        "subheading": "Para cafes, bares e restaurantes. Mesas, gorjetas e checkout rapido.",
                        "cta_primary_text": "Ver parceiros",
                        "cta_secondary_text": "Pedir recomendacao",
                    },
                    "main": {
                        "heading": "Para o servico",
                        "body": "Gestao de mesas, contas divididas e tickets de cozinha.",
                    },
                    "cta": {
                        "heading": "Precisa de uma lista curta?",
                        "body": "Diga o seu tipo de negocio e sugerimos opcoes.",
                        "cta_primary_text": "Pedir recomendacao",
                        "cta_primary_url": "/help-center/",
                    },
                    "affiliate_disclosure": {
                        "body": "Alguns links podem ser de afiliados. Isso nao altera o preco.",
                    },
                    **pos_affiliate_translations["pt"],
                },
            },
            "pos-systems-services": {
                "en": {
                    "title": "POS for Services",
                    "nav_label": "POS for Services",
                    "meta_title": "POS for Services",
                    "meta_description": "POS options for appointments, invoices, and simple payments.",
                    "hero": {
                        "heading": "POS for Services",
                        "subheading": "For appointments, invoices, and simple payments.",
                        "cta_primary_text": "View partners",
                        "cta_secondary_text": "Get a recommendation",
                    },
                    "main": {
                        "heading": "Built for bookings",
                        "body": "Look for scheduling, deposits, and easy invoicing.",
                    },
                    "cta": {
                        "heading": "Need a shortlist?",
                        "body": "Tell us your service type and we will suggest options.",
                        "cta_primary_text": "Get a recommendation",
                        "cta_primary_url": "/help-center/",
                    },
                    "affiliate_disclosure": {
                        "body": "Some links may be affiliate links. This does not change the price you pay.",
                    },
                    **pos_affiliate_translations["en"],
                },
                "nl": {
                    "title": "POS voor services",
                    "nav_label": "POS voor services",
                    "meta_title": "POS voor services",
                    "meta_description": "POS opties voor afspraken, facturen en eenvoudige betalingen.",
                    "hero": {
                        "heading": "POS voor services",
                        "subheading": "Voor afspraken, facturen en eenvoudige betalingen.",
                        "cta_primary_text": "Bekijk partners",
                        "cta_secondary_text": "Krijg advies",
                    },
                    "main": {
                        "heading": "Voor afspraken",
                        "body": "Kijk naar planning, aanbetalingen en eenvoudige facturen.",
                    },
                    "cta": {
                        "heading": "Korte lijst nodig?",
                        "body": "Vertel je type dienst en we geven opties.",
                        "cta_primary_text": "Krijg advies",
                        "cta_primary_url": "/help-center/",
                    },
                    "affiliate_disclosure": {
                        "body": "Sommige links kunnen affiliate links zijn. Dit verandert de prijs niet.",
                    },
                    **pos_affiliate_translations["nl"],
                },
                "fr": {
                    "title": "POS pour services",
                    "nav_label": "POS pour services",
                    "meta_title": "POS pour services",
                    "meta_description": "Options POS pour rendez-vous, factures et paiements simples.",
                    "hero": {
                        "heading": "POS pour services",
                        "subheading": "Pour rendez-vous, factures et paiements simples.",
                        "cta_primary_text": "Voir les partenaires",
                        "cta_secondary_text": "Demander un conseil",
                    },
                    "main": {
                        "heading": "Pense pour les rendez-vous",
                        "body": "Planning, acomptes et facturation simple.",
                    },
                    "cta": {
                        "heading": "Besoin d'une selection?",
                        "body": "Dites votre type de service et nous proposerons des options.",
                        "cta_primary_text": "Demander un conseil",
                        "cta_primary_url": "/help-center/",
                    },
                    "affiliate_disclosure": {
                        "body": "Certains liens peuvent etre des liens d'affiliation. Cela ne change pas le prix.",
                    },
                    **pos_affiliate_translations["fr"],
                },
                "de": {
                    "title": "POS fuer Services",
                    "nav_label": "POS fuer Services",
                    "meta_title": "POS fuer Services",
                    "meta_description": "POS Optionen fuer Termine, Rechnungen und einfache Zahlungen.",
                    "hero": {
                        "heading": "POS fuer Services",
                        "subheading": "Fuer Termine, Rechnungen und einfache Zahlungen.",
                        "cta_primary_text": "Partner ansehen",
                        "cta_secondary_text": "Empfehlung erhalten",
                    },
                    "main": {
                        "heading": "Fuer Termine",
                        "body": "Terminplanung, Anzahlungen und einfache Rechnungen.",
                    },
                    "cta": {
                        "heading": "Kurzliste gesucht?",
                        "body": "Nennen Sie Ihren Service und wir schlagen Optionen vor.",
                        "cta_primary_text": "Empfehlung erhalten",
                        "cta_primary_url": "/help-center/",
                    },
                    "affiliate_disclosure": {
                        "body": "Einige Links koennen Affiliate-Links sein. Das aendert den Preis nicht.",
                    },
                    **pos_affiliate_translations["de"],
                },
                "es": {
                    "title": "POS para servicios",
                    "nav_label": "POS para servicios",
                    "meta_title": "POS para servicios",
                    "meta_description": "Opciones POS para citas, facturas y pagos simples.",
                    "hero": {
                        "heading": "POS para servicios",
                        "subheading": "Para citas, facturas y pagos simples.",
                        "cta_primary_text": "Ver partners",
                        "cta_secondary_text": "Pedir recomendacion",
                    },
                    "main": {
                        "heading": "Pensado para citas",
                        "body": "Agenda, depositos y facturacion simple.",
                    },
                    "cta": {
                        "heading": "Necesitas una lista corta?",
                        "body": "Dinos tu tipo de servicio y sugerimos opciones.",
                        "cta_primary_text": "Pedir recomendacion",
                        "cta_primary_url": "/help-center/",
                    },
                    "affiliate_disclosure": {
                        "body": "Algunos enlaces pueden ser de afiliados. No cambia el precio.",
                    },
                    **pos_affiliate_translations["es"],
                },
                "pt": {
                    "title": "POS para servicos",
                    "nav_label": "POS para servicos",
                    "meta_title": "POS para servicos",
                    "meta_description": "Opcoes POS para marcacoes, faturas e pagamentos simples.",
                    "hero": {
                        "heading": "POS para servicos",
                        "subheading": "Para marcacoes, faturas e pagamentos simples.",
                        "cta_primary_text": "Ver parceiros",
                        "cta_secondary_text": "Pedir recomendacao",
                    },
                    "main": {
                        "heading": "Feito para marcacoes",
                        "body": "Agenda, depositos e faturacao simples.",
                    },
                    "cta": {
                        "heading": "Precisa de uma lista curta?",
                        "body": "Diga o seu tipo de servico e sugerimos opcoes.",
                        "cta_primary_text": "Pedir recomendacao",
                        "cta_primary_url": "/help-center/",
                    },
                    "affiliate_disclosure": {
                        "body": "Alguns links podem ser de afiliados. Isso nao altera o preco.",
                    },
                    **pos_affiliate_translations["pt"],
                },
            },
            "pos-systems-compare": {
                "en": {
                    "title": "Compare POS options",
                    "nav_label": "Compare POS",
                    "meta_title": "Compare POS options",
                    "meta_description": "A simple POS comparison page.",
                    "hero": {
                        "heading": "Compare POS options",
                        "subheading": "A simple overview to help you decide.",
                        "cta_primary_text": "Get a recommendation",
                        "cta_secondary_text": "",
                    },
                    "main": {
                        "heading": "Coming soon",
                        "body": "We are preparing a clear comparison table. For now, ask for a recommendation.",
                    },
                    "cta": {
                        "heading": "Not sure yet?",
                        "body": "We can help you compare the basics for your business.",
                        "cta_primary_text": "Get a recommendation",
                        "cta_primary_url": "/help-center/",
                    },
                    "affiliate_disclosure": {
                        "body": "Some links may be affiliate links. This does not change the price you pay.",
                    },
                },
                "nl": {
                    "title": "POS vergelijken",
                    "nav_label": "POS vergelijken",
                    "meta_title": "POS vergelijken",
                    "meta_description": "Een eenvoudige POS vergelijking.",
                    "hero": {
                        "heading": "POS vergelijken",
                        "subheading": "Een simpel overzicht om te kiezen.",
                        "cta_primary_text": "Krijg advies",
                        "cta_secondary_text": "",
                    },
                    "main": {
                        "heading": "Binnenkort",
                        "body": "We maken een duidelijke vergelijking. Vraag nu om advies.",
                    },
                    "cta": {
                        "heading": "Niet zeker?",
                        "body": "We helpen je de basis te vergelijken.",
                        "cta_primary_text": "Krijg advies",
                        "cta_primary_url": "/help-center/",
                    },
                    "affiliate_disclosure": {
                        "body": "Sommige links kunnen affiliate links zijn. Dit verandert de prijs niet.",
                    },
                },
                "fr": {
                    "title": "Comparer POS",
                    "nav_label": "Comparer POS",
                    "meta_title": "Comparer POS",
                    "meta_description": "Une page simple de comparaison POS.",
                    "hero": {
                        "heading": "Comparer POS",
                        "subheading": "Un apercu simple pour choisir.",
                        "cta_primary_text": "Demander un conseil",
                        "cta_secondary_text": "",
                    },
                    "main": {
                        "heading": "Bientot",
                        "body": "Nous preparons une comparaison claire. Pour l'instant, demandez un conseil.",
                    },
                    "cta": {
                        "heading": "Pas certain?",
                        "body": "Nous aidons a comparer les bases.",
                        "cta_primary_text": "Demander un conseil",
                        "cta_primary_url": "/help-center/",
                    },
                    "affiliate_disclosure": {
                        "body": "Certains liens peuvent etre des liens d'affiliation. Cela ne change pas le prix.",
                    },
                },
                "de": {
                    "title": "POS vergleichen",
                    "nav_label": "POS vergleichen",
                    "meta_title": "POS vergleichen",
                    "meta_description": "Eine einfache POS Vergleichsseite.",
                    "hero": {
                        "heading": "POS vergleichen",
                        "subheading": "Ein kurzer Ueberblick zur Entscheidung.",
                        "cta_primary_text": "Empfehlung erhalten",
                        "cta_secondary_text": "",
                    },
                    "main": {
                        "heading": "Kommt bald",
                        "body": "Wir bereiten eine klare Vergleichstabelle vor. Fragen Sie bis dahin nach einer Empfehlung.",
                    },
                    "cta": {
                        "heading": "Noch unsicher?",
                        "body": "Wir helfen beim Vergleich der Grundlagen.",
                        "cta_primary_text": "Empfehlung erhalten",
                        "cta_primary_url": "/help-center/",
                    },
                    "affiliate_disclosure": {
                        "body": "Einige Links koennen Affiliate-Links sein. Das aendert den Preis nicht.",
                    },
                },
                "es": {
                    "title": "Comparar POS",
                    "nav_label": "Comparar POS",
                    "meta_title": "Comparar POS",
                    "meta_description": "Una pagina simple para comparar POS.",
                    "hero": {
                        "heading": "Comparar POS",
                        "subheading": "Un resumen simple para elegir.",
                        "cta_primary_text": "Pedir recomendacion",
                        "cta_secondary_text": "",
                    },
                    "main": {
                        "heading": "Proximamente",
                        "body": "Estamos preparando una tabla clara. Por ahora, pide recomendacion.",
                    },
                    "cta": {
                        "heading": "No estas seguro?",
                        "body": "Te ayudamos a comparar lo basico.",
                        "cta_primary_text": "Pedir recomendacion",
                        "cta_primary_url": "/help-center/",
                    },
                    "affiliate_disclosure": {
                        "body": "Algunos enlaces pueden ser de afiliados. No cambia el precio.",
                    },
                },
                "pt": {
                    "title": "Comparar POS",
                    "nav_label": "Comparar POS",
                    "meta_title": "Comparar POS",
                    "meta_description": "Uma pagina simples para comparar POS.",
                    "hero": {
                        "heading": "Comparar POS",
                        "subheading": "Um resumo simples para escolher.",
                        "cta_primary_text": "Pedir recomendacao",
                        "cta_secondary_text": "",
                    },
                    "main": {
                        "heading": "Em breve",
                        "body": "Estamos a preparar uma tabela clara. Para ja, peça recomendacao.",
                    },
                    "cta": {
                        "heading": "Nao tem a certeza?",
                        "body": "Ajudamos a comparar o basico.",
                        "cta_primary_text": "Pedir recomendacao",
                        "cta_primary_url": "/help-center/",
                    },
                    "affiliate_disclosure": {
                        "body": "Alguns links podem ser de afiliados. Isso nao altera o preco.",
                    },
                },
            },
            "pos-systems-faq": {
                "en": {
                    "title": "POS FAQ",
                    "nav_label": "POS FAQ",
                    "meta_title": "POS FAQ",
                    "meta_description": "Simple POS answers in plain language.",
                    "hero": {
                        "heading": "POS FAQ",
                        "subheading": "Simple answers in plain language.",
                        "cta_primary_text": "Get a recommendation",
                        "cta_secondary_text": "",
                    },
                    "main": {
                        "heading": "Common questions",
                        "body": "Quick guidance before you choose a POS.",
                    },
                    "cta": {
                        "heading": "Need help choosing?",
                        "body": "We can point you to practical options.",
                        "cta_primary_text": "Get a recommendation",
                        "cta_primary_url": "/help-center/",
                    },
                    "affiliate_disclosure": {
                        "body": "Some links may be affiliate links. This does not change the price you pay.",
                    },
                    "faq_items": [
                        {"heading": "What is a POS system?", "body": "It is the software and hardware used to take payments and track sales."},
                        {"heading": "Do I need a card terminal?", "body": "Most POS work with a simple card reader or a phone, depending on the provider."},
                        {"heading": "Can a POS help with inventory?", "body": "Retail POS usually include basic stock tracking and low stock alerts."},
                        {"heading": "Are there monthly fees?", "body": "Many providers charge a monthly plan, plus payment processing fees."},
                        {"heading": "Can I use my own devices?", "body": "Many POS systems work on tablets you already own."},
                        {"heading": "Is support included?", "body": "Most providers include email or chat support. Higher plans may add phone support."},
                    ],
                },
                "nl": {
                    "title": "POS FAQ",
                    "nav_label": "POS FAQ",
                    "meta_title": "POS FAQ",
                    "meta_description": "Eenvoudige POS antwoorden.",
                    "hero": {
                        "heading": "POS FAQ",
                        "subheading": "Eenvoudige antwoorden.",
                        "cta_primary_text": "Krijg advies",
                        "cta_secondary_text": "",
                    },
                    "main": {
                        "heading": "Veelgestelde vragen",
                        "body": "Snelle uitleg voor je kiest.",
                    },
                    "cta": {
                        "heading": "Hulp nodig?",
                        "body": "We wijzen je op praktische opties.",
                        "cta_primary_text": "Krijg advies",
                        "cta_primary_url": "/help-center/",
                    },
                    "affiliate_disclosure": {
                        "body": "Sommige links kunnen affiliate links zijn. Dit verandert de prijs niet.",
                    },
                    "faq_items": [
                        {"heading": "Wat is een POS systeem?", "body": "Het is software en hardware voor betalingen en verkoopoverzicht."},
                        {"heading": "Heb ik een kaartlezer nodig?", "body": "Meestal wel, of een telefoon, afhankelijk van de aanbieder."},
                        {"heading": "Helpt een POS met voorraad?", "body": "Retail POS heeft vaak basis voorraad en meldingen bij lage stock."},
                        {"heading": "Zijn er maandelijkse kosten?", "body": "Veel aanbieders rekenen een maandbedrag plus transactiekosten."},
                        {"heading": "Kan ik eigen apparaten gebruiken?", "body": "Veel POS systemen werken op tablets die je al hebt."},
                        {"heading": "Is er support?", "body": "Meestal via email of chat. Hogere plannen bieden soms telefoon."},
                    ],
                },
                "fr": {
                    "title": "FAQ POS",
                    "nav_label": "FAQ POS",
                    "meta_title": "FAQ POS",
                    "meta_description": "Reponses POS simples.",
                    "hero": {
                        "heading": "FAQ POS",
                        "subheading": "Reponses simples.",
                        "cta_primary_text": "Demander un conseil",
                        "cta_secondary_text": "",
                    },
                    "main": {
                        "heading": "Questions courantes",
                        "body": "Explications rapides avant de choisir.",
                    },
                    "cta": {
                        "heading": "Besoin d'aide?",
                        "body": "Nous indiquons des options pratiques.",
                        "cta_primary_text": "Demander un conseil",
                        "cta_primary_url": "/help-center/",
                    },
                    "affiliate_disclosure": {
                        "body": "Certains liens peuvent etre des liens d'affiliation. Cela ne change pas le prix.",
                    },
                    "faq_items": [
                        {"heading": "Qu'est-ce qu'un POS?", "body": "Logiciel et materiel pour encaisser et suivre les ventes."},
                        {"heading": "Faut-il un terminal carte?", "body": "Souvent oui, ou un telephone, selon le fournisseur."},
                        {"heading": "Le POS aide-t-il le stock?", "body": "Le POS retail offre souvent un stock de base et alertes."},
                        {"heading": "Y a-t-il des frais mensuels?", "body": "Beaucoup facturent un abonnement et des frais de transaction."},
                        {"heading": "Puis-je utiliser mes appareils?", "body": "Beaucoup de POS fonctionnent sur des tablettes existantes."},
                        {"heading": "Le support est-il inclus?", "body": "Souvent email ou chat. Les plans superieurs ajoutent le telephone."},
                    ],
                },
                "de": {
                    "title": "POS FAQ",
                    "nav_label": "POS FAQ",
                    "meta_title": "POS FAQ",
                    "meta_description": "Einfache POS Antworten.",
                    "hero": {
                        "heading": "POS FAQ",
                        "subheading": "Einfache Antworten.",
                        "cta_primary_text": "Empfehlung erhalten",
                        "cta_secondary_text": "",
                    },
                    "main": {
                        "heading": "Hauefige Fragen",
                        "body": "Kurze Antworten vor der Auswahl.",
                    },
                    "cta": {
                        "heading": "Hilfe bei der Auswahl?",
                        "body": "Wir zeigen praktische Optionen.",
                        "cta_primary_text": "Empfehlung erhalten",
                        "cta_primary_url": "/help-center/",
                    },
                    "affiliate_disclosure": {
                        "body": "Einige Links koennen Affiliate-Links sein. Das aendert den Preis nicht.",
                    },
                    "faq_items": [
                        {"heading": "Was ist ein POS System?", "body": "Software und Hardware fuer Zahlungen und Verkaufsuebersicht."},
                        {"heading": "Brauche ich ein Kartenterminal?", "body": "Meist ja, oder ein Handy, je nach Anbieter."},
                        {"heading": "Hilft POS beim Bestand?", "body": "Retail POS bietet oft Basisbestand und Warnungen."},
                        {"heading": "Gibt es Monatsgebuehren?", "body": "Viele Anbieter verlangen eine Monatsgebuehr plus Transaktionsgebuehren."},
                        {"heading": "Kann ich eigene Geraete nutzen?", "body": "Viele POS Systeme laufen auf vorhandenen Tablets."},
                        {"heading": "Ist Support enthalten?", "body": "Meist per Email oder Chat. Hoehere Plaene bieten Telefon."},
                    ],
                },
                "es": {
                    "title": "FAQ POS",
                    "nav_label": "FAQ POS",
                    "meta_title": "FAQ POS",
                    "meta_description": "Respuestas POS simples.",
                    "hero": {
                        "heading": "FAQ POS",
                        "subheading": "Respuestas simples.",
                        "cta_primary_text": "Pedir recomendacion",
                        "cta_secondary_text": "",
                    },
                    "main": {
                        "heading": "Preguntas comunes",
                        "body": "Guia rapida antes de elegir.",
                    },
                    "cta": {
                        "heading": "Necesitas ayuda?",
                        "body": "Te mostramos opciones practicas.",
                        "cta_primary_text": "Pedir recomendacion",
                        "cta_primary_url": "/help-center/",
                    },
                    "affiliate_disclosure": {
                        "body": "Algunos enlaces pueden ser de afiliados. No cambia el precio.",
                    },
                    "faq_items": [
                        {"heading": "Que es un POS?", "body": "Software y hardware para cobrar y seguir ventas."},
                        {"heading": "Necesito un terminal de tarjeta?", "body": "Normalmente si, o un telefono, segun el proveedor."},
                        {"heading": "Ayuda el POS con inventario?", "body": "El POS retail suele incluir stock basico y alertas."},
                        {"heading": "Hay cuotas mensuales?", "body": "Muchos proveedores cobran plan mensual y comisiones."},
                        {"heading": "Puedo usar mis dispositivos?", "body": "Muchos POS funcionan en tablets que ya tienes."},
                        {"heading": "El soporte esta incluido?", "body": "Normalmente email o chat. Planes altos incluyen telefono."},
                    ],
                },
                "pt": {
                    "title": "FAQ POS",
                    "nav_label": "FAQ POS",
                    "meta_title": "FAQ POS",
                    "meta_description": "Respostas POS simples.",
                    "hero": {
                        "heading": "FAQ POS",
                        "subheading": "Respostas simples.",
                        "cta_primary_text": "Pedir recomendacao",
                        "cta_secondary_text": "",
                    },
                    "main": {
                        "heading": "Perguntas comuns",
                        "body": "Guia rapido antes de escolher.",
                    },
                    "cta": {
                        "heading": "Precisa de ajuda?",
                        "body": "Mostramos opcoes praticas.",
                        "cta_primary_text": "Pedir recomendacao",
                        "cta_primary_url": "/help-center/",
                    },
                    "affiliate_disclosure": {
                        "body": "Alguns links podem ser de afiliados. Isso nao altera o preco.",
                    },
                    "faq_items": [
                        {"heading": "O que e um POS?", "body": "Software e hardware para cobrar e acompanhar vendas."},
                        {"heading": "Preciso de terminal de cartao?", "body": "Normalmente sim, ou um telefone, depende do fornecedor."},
                        {"heading": "O POS ajuda com stock?", "body": "POS de retalho costuma ter stock basico e alertas."},
                        {"heading": "Existem taxas mensais?", "body": "Muitos fornecedores cobram plano mensal e taxas."},
                        {"heading": "Posso usar os meus dispositivos?", "body": "Muitos POS funcionam em tablets que ja tem."},
                        {"heading": "O suporte esta incluido?", "body": "Normalmente email ou chat. Planos superiores incluem telefone."},
                    ],
                },
            },
        }

        page_translations.update(pos_pages_translations)

        product_names = {
            "en": {
                "products": "Products",
                "websites": "Websites",
                "seo": "SEO",
                "print_studio": "Print Studio",
                "pos_systems": "Card Payments",
                "ads": "Ads",
                "uptime": "Uptime Status",
                "support": "Support",
                "maintenance": "Maintenance",
                "ecommerce": "Ecommerce",
            },
            "nl": {
                "products": "Producten",
                "websites": "Websites",
                "seo": "SEO",
                "print_studio": "Print Studio",
                "pos_systems": "POS-systemen",
                "ads": "Ads",
                "uptime": "Uptime status",
                "support": "Support",
                "maintenance": "Onderhoud",
                "ecommerce": "Ecommerce",
            },
            "fr": {
                "products": "Produits",
                "websites": "Sites web",
                "seo": "SEO",
                "print_studio": "Print Studio",
                "pos_systems": "Systemes POS",
                "ads": "Ads",
                "uptime": "Statut uptime",
                "support": "Support",
                "maintenance": "Maintenance",
                "ecommerce": "Ecommerce",
            },
            "de": {
                "products": "Produkte",
                "websites": "Websites",
                "seo": "SEO",
                "print_studio": "Print Studio",
                "pos_systems": "POS-Systeme",
                "ads": "Ads",
                "uptime": "Uptime Status",
                "support": "Support",
                "maintenance": "Wartung",
                "ecommerce": "Ecommerce",
            },
            "es": {
                "products": "Productos",
                "websites": "Websites",
                "seo": "SEO",
                "print_studio": "Print Studio",
                "pos_systems": "Sistemas POS",
                "ads": "Ads",
                "uptime": "Estado uptime",
                "support": "Soporte",
                "maintenance": "Mantenimiento",
                "ecommerce": "Ecommerce",
            },
            "pt": {
                "products": "Produtos",
                "websites": "Websites",
                "seo": "SEO",
                "print_studio": "Print Studio",
                "pos_systems": "Sistemas POS",
                "ads": "Ads",
                "uptime": "Estado uptime",
                "support": "Suporte",
                "maintenance": "Manutencao",
                "ecommerce": "Ecommerce",
            },
        }

        product_copy = {
            "en": {
                "index_heading": "Products for small businesses.",
                "index_subheading": "Pick the tools you need and grow from there.",
                "product_heading": "%(name)s for modern teams.",
                "product_subheading": "Short, practical setup and support.",
                "main_heading": "What you get",
                "main_body": "Clear features, simple pricing, and fast setup.",
                "cta_primary": "Talk to us",
                "cta_secondary": "See plans",
            },
            "nl": {
                "index_heading": "Producten voor kleine bedrijven.",
                "index_subheading": "Kies wat je nodig hebt en groei verder.",
                "product_heading": "%(name)s voor moderne teams.",
                "product_subheading": "Praktische setup en support.",
                "main_heading": "Wat je krijgt",
                "main_body": "Duidelijke features, simpele prijzen, snelle start.",
                "cta_primary": "Neem contact op",
                "cta_secondary": "Bekijk plannen",
            },
            "fr": {
                "index_heading": "Produits pour petites entreprises.",
                "index_subheading": "Choisissez les bons outils et evoluez.",
                "product_heading": "%(name)s pour equipes modernes.",
                "product_subheading": "Mise en place simple et support.",
                "main_heading": "Ce que vous obtenez",
                "main_body": "Fonctions claires, prix simples, demarrage rapide.",
                "cta_primary": "Parlons-en",
                "cta_secondary": "Voir les offres",
            },
            "de": {
                "index_heading": "Produkte fuer kleine Unternehmen.",
                "index_subheading": "Waehlen Sie die passenden Tools.",
                "product_heading": "%(name)s fuer moderne Teams.",
                "product_subheading": "Einfache Einrichtung und Support.",
                "main_heading": "Was Sie bekommen",
                "main_body": "Klare Features, einfache Preise, schneller Start.",
                "cta_primary": "Kontakt aufnehmen",
                "cta_secondary": "Plaene ansehen",
            },
            "es": {
                "index_heading": "Productos para pequenos negocios.",
                "index_subheading": "Elige los tools y crece.",
                "product_heading": "%(name)s para equipos modernos.",
                "product_subheading": "Setup rapido y soporte.",
                "main_heading": "Lo que obtienes",
                "main_body": "Funciones claras, precios simples, inicio rapido.",
                "cta_primary": "Hablar con nosotros",
                "cta_secondary": "Ver planes",
            },
            "pt": {
                "index_heading": "Produtos para pequenos negocios.",
                "index_subheading": "Escolha os tools e cresca.",
                "product_heading": "%(name)s para equipas modernas.",
                "product_subheading": "Setup rapido e suporte.",
                "main_heading": "O que recebe",
                "main_body": "Funcoes claras, precos simples, arranque rapido.",
                "cta_primary": "Fale connosco",
                "cta_secondary": "Ver planos",
            },
        }

        product_pages = [
            ("products", "products", True),
            ("products-websites", "websites", False),
            ("products-seo", "seo", False),
            ("products-print-studio", "print_studio", False),
            ("products-pos-systems", "pos_systems", False),
            ("products-ads", "ads", False),
            ("products-uptime-status", "uptime", False),
            ("products-support", "support", False),
            ("products-maintenance", "maintenance", False),
            ("products-ecommerce", "ecommerce", False),
        ]

        product_translations = {}
        for slug, name_key, show_in_nav in product_pages:
            product_translations[slug] = {}
            for lang in languages:
                name = product_names[lang][name_key]
                copy = product_copy[lang]
                hero_heading = (
                    copy["index_heading"]
                    if slug == "products"
                    else copy["product_heading"] % {"name": name}
                )
                hero_subheading = (
                    copy["index_subheading"]
                    if slug == "products"
                    else copy["product_subheading"]
                )
                menu_subtitle = hero_subheading
                product_translations[slug][lang] = {
                    "title": name,
                    "nav_label": name if show_in_nav else "",
                    "menu_subtitle": menu_subtitle,
                    "meta_title": name,
                    "meta_description": copy["main_body"],
                    "hero": {
                        "heading": hero_heading,
                        "subheading": hero_subheading,
                        "cta_primary_text": copy["cta_primary"],
                        "cta_secondary_text": copy["cta_secondary"],
                    },
                    "main": {
                        "heading": copy["main_heading"],
                        "body": copy["main_body"],
                    },
                    "cta": {"cta_primary_text": copy["cta_primary"]},
                }

        page_translations.update(product_translations)

        websites_plan_pages = {
            "websites-one-page": {
                "en": {
                    "title": "One Page Website",
                    "nav_label": "One Page",
                    "menu_subtitle": "Fast single-page site.",
                    "hero_subheading": "Single page site for a quick launch.",
                    "main_body": "One page, clear CTA, fast setup.",
                },
                "nl": {
                    "title": "One Page Website",
                    "nav_label": "One Page",
                    "menu_subtitle": "Snelle one-page site.",
                    "hero_subheading": "One page site voor snelle start.",
                    "main_body": "Een pagina, duidelijke CTA, snelle start.",
                },
                "fr": {
                    "title": "Site one page",
                    "nav_label": "One Page",
                    "menu_subtitle": "Site one page rapide.",
                    "hero_subheading": "Site en une page pour lancer vite.",
                    "main_body": "Une page, CTA claire, mise en place rapide.",
                },
                "de": {
                    "title": "One Page Website",
                    "nav_label": "One Page",
                    "menu_subtitle": "Schnelle One-Page Seite.",
                    "hero_subheading": "One-Page Seite fuer schnellen Start.",
                    "main_body": "Eine Seite, klare CTA, schneller Start.",
                },
                "es": {
                    "title": "One Page Website",
                    "nav_label": "One Page",
                    "menu_subtitle": "One page rapida.",
                    "hero_subheading": "One page para lanzar rapido.",
                    "main_body": "Una pagina, CTA clara, inicio rapido.",
                },
                "pt": {
                    "title": "One Page Website",
                    "nav_label": "One Page",
                    "menu_subtitle": "One page rapida.",
                    "hero_subheading": "One page para arrancar rapido.",
                    "main_body": "Uma pagina, CTA clara, arranque rapido.",
                },
            },
            "websites-multi-page": {
                "en": {
                    "title": "Multi Page Website",
                    "nav_label": "Multi Page",
                    "menu_subtitle": "Multiple pages for services.",
                    "hero_subheading": "Separate pages for services and teams.",
                    "main_body": "Add pages as your business grows.",
                },
                "nl": {
                    "title": "Multi Page Website",
                    "nav_label": "Multi Page",
                    "menu_subtitle": "Meerdere paginas voor diensten.",
                    "hero_subheading": "Losse paginas voor diensten en teams.",
                    "main_body": "Voeg paginas toe als je groeit.",
                },
                "fr": {
                    "title": "Site multi pages",
                    "nav_label": "Multi Page",
                    "menu_subtitle": "Plusieurs pages pour services.",
                    "hero_subheading": "Pages separees pour services et equipe.",
                    "main_body": "Ajoutez des pages quand vous grandissez.",
                },
                "de": {
                    "title": "Multi Page Website",
                    "nav_label": "Multi Page",
                    "menu_subtitle": "Mehrere Seiten fuer Services.",
                    "hero_subheading": "Getrennte Seiten fuer Services und Teams.",
                    "main_body": "Fuegen Sie Seiten hinzu, wenn Sie wachsen.",
                },
                "es": {
                    "title": "Website multi pagina",
                    "nav_label": "Multi Page",
                    "menu_subtitle": "Varias paginas para servicios.",
                    "hero_subheading": "Paginas separadas para servicios y equipo.",
                    "main_body": "Agrega paginas cuando crezca tu negocio.",
                },
                "pt": {
                    "title": "Website multi pagina",
                    "nav_label": "Multi Page",
                    "menu_subtitle": "Varias paginas para servicos.",
                    "hero_subheading": "Paginas separadas para servicos e equipa.",
                    "main_body": "Adicione paginas quando o negocio crescer.",
                },
            },
            "websites-multi-page-seo": {
                "en": {
                    "title": "Multi Page + SEO",
                    "nav_label": "Multi Page + SEO",
                    "menu_subtitle": "Multi-page plus SEO setup.",
                    "hero_subheading": "Structured pages with SEO-ready setup.",
                    "main_body": "Metadata and structure for local search.",
                },
                "nl": {
                    "title": "Multi Page + SEO",
                    "nav_label": "Multi Page + SEO",
                    "menu_subtitle": "Multi page met SEO basis.",
                    "hero_subheading": "Structuur met SEO basis.",
                    "main_body": "Metadata en structuur voor lokale zoekresultaten.",
                },
                "fr": {
                    "title": "Multi pages + SEO",
                    "nav_label": "Multi Page + SEO",
                    "menu_subtitle": "Multi pages avec base SEO.",
                    "hero_subheading": "Structure avec base SEO.",
                    "main_body": "Meta et structure pour recherche locale.",
                },
                "de": {
                    "title": "Multi Page + SEO",
                    "nav_label": "Multi Page + SEO",
                    "menu_subtitle": "Multi Page mit SEO Basis.",
                    "hero_subheading": "Struktur mit SEO Basis.",
                    "main_body": "Meta und Struktur fuer lokale Suche.",
                },
                "es": {
                    "title": "Multi pagina + SEO",
                    "nav_label": "Multi Page + SEO",
                    "menu_subtitle": "Multi pagina con base SEO.",
                    "hero_subheading": "Estructura con base SEO.",
                    "main_body": "Meta y estructura para busqueda local.",
                },
                "pt": {
                    "title": "Multi pagina + SEO",
                    "nav_label": "Multi Page + SEO",
                    "menu_subtitle": "Multi pagina com base SEO.",
                    "hero_subheading": "Estrutura com base SEO.",
                    "main_body": "Meta e estrutura para pesquisa local.",
                },
            },
            "websites-catalog-site": {
                "en": {
                    "title": "Catalog Site",
                    "nav_label": "Catalog Site",
                    "menu_subtitle": "No orders or payments.",
                    "hero_subheading": "Products with optional prices. No orders, no payments.",
                    "main_body": "Catalog only. Prices optional. No checkout.",
                },
                "nl": {
                    "title": "Catalogus site",
                    "nav_label": "Catalog Site",
                    "menu_subtitle": "Geen orders of betalingen.",
                    "hero_subheading": "Producten met optionele prijzen. Geen orders, geen betalingen.",
                    "main_body": "Alleen catalogus. Prijzen optioneel. Geen checkout.",
                },
                "fr": {
                    "title": "Site catalogue",
                    "nav_label": "Catalog Site",
                    "menu_subtitle": "Sans commandes ni paiements.",
                    "hero_subheading": "Produits avec prix optionnels. Pas de commandes, pas de paiements.",
                    "main_body": "Catalogue uniquement. Prix optionnels. Pas de checkout.",
                },
                "de": {
                    "title": "Katalog Seite",
                    "nav_label": "Catalog Site",
                    "menu_subtitle": "Keine Bestellungen oder Zahlungen.",
                    "hero_subheading": "Produkte mit optionalen Preisen. Keine Bestellungen, keine Zahlungen.",
                    "main_body": "Nur Katalog. Preise optional. Kein Checkout.",
                },
                "es": {
                    "title": "Sitio catalogo",
                    "nav_label": "Catalog Site",
                    "menu_subtitle": "Sin pedidos ni pagos.",
                    "hero_subheading": "Productos con precios opcionales. Sin pedidos, sin pagos.",
                    "main_body": "Solo catalogo. Precios opcionales. Sin checkout.",
                },
                "pt": {
                    "title": "Site catalogo",
                    "nav_label": "Catalog Site",
                    "menu_subtitle": "Sem encomendas nem pagamentos.",
                    "hero_subheading": "Produtos com precos opcionais. Sem encomendas, sem pagamentos.",
                    "main_body": "So catalogo. Precos opcionais. Sem checkout.",
                },
            },
            "websites-eshop-starter": {
                "en": {
                    "title": "Starter eShop",
                    "nav_label": "Starter eShop",
                    "menu_subtitle": "One-page shop up to 8 products.",
                    "hero_subheading": "One-page shop with up to 8 products.",
                    "main_body": "Single page shop for up to 8 products.",
                },
                "nl": {
                    "title": "Starter eShop",
                    "nav_label": "Starter eShop",
                    "menu_subtitle": "One-page shop tot 8 producten.",
                    "hero_subheading": "One-page shop met tot 8 producten.",
                    "main_body": "Een pagina shop tot 8 producten.",
                },
                "fr": {
                    "title": "eShop starter",
                    "nav_label": "Starter eShop",
                    "menu_subtitle": "Boutique one page jusqu a 8 produits.",
                    "hero_subheading": "Boutique one page jusqu a 8 produits.",
                    "main_body": "Boutique une page pour 8 produits max.",
                },
                "de": {
                    "title": "Starter eShop",
                    "nav_label": "Starter eShop",
                    "menu_subtitle": "One-Page Shop bis 8 Produkte.",
                    "hero_subheading": "One-Page Shop mit bis zu 8 Produkten.",
                    "main_body": "Einseitiger Shop bis 8 Produkte.",
                },
                "es": {
                    "title": "eShop starter",
                    "nav_label": "Starter eShop",
                    "menu_subtitle": "Tienda one page hasta 8 productos.",
                    "hero_subheading": "Tienda one page con hasta 8 productos.",
                    "main_body": "Tienda de una pagina hasta 8 productos.",
                },
                "pt": {
                    "title": "eShop starter",
                    "nav_label": "Starter eShop",
                    "menu_subtitle": "Loja one page ate 8 produtos.",
                    "hero_subheading": "Loja one page com ate 8 produtos.",
                    "main_body": "Loja de uma pagina ate 8 produtos.",
                },
            },
            "websites-eshop-premium": {
                "en": {
                    "title": "Premium Shop",
                    "nav_label": "Premium Shop",
                    "menu_subtitle": "Unlimited products and all features.",
                    "hero_subheading": "Unlimited products with all features.",
                    "main_body": "Full ecommerce with all features.",
                },
                "nl": {
                    "title": "Premium Shop",
                    "nav_label": "Premium Shop",
                    "menu_subtitle": "Onbeperkte producten en features.",
                    "hero_subheading": "Onbeperkt aantal producten en alle features.",
                    "main_body": "Volledige ecommerce met alle features.",
                },
                "fr": {
                    "title": "Boutique premium",
                    "nav_label": "Premium Shop",
                    "menu_subtitle": "Produits illimites et toutes fonctions.",
                    "hero_subheading": "Produits illimites et toutes les fonctions.",
                    "main_body": "Ecommerce complet avec toutes les fonctions.",
                },
                "de": {
                    "title": "Premium Shop",
                    "nav_label": "Premium Shop",
                    "menu_subtitle": "Unbegrenzte Produkte und Features.",
                    "hero_subheading": "Unbegrenzte Produkte und alle Features.",
                    "main_body": "Volles Ecommerce mit allen Features.",
                },
                "es": {
                    "title": "Tienda premium",
                    "nav_label": "Premium Shop",
                    "menu_subtitle": "Productos ilimitados y funciones.",
                    "hero_subheading": "Productos ilimitados y todas las funciones.",
                    "main_body": "Ecommerce completo con todas las funciones.",
                },
                "pt": {
                    "title": "Loja premium",
                    "nav_label": "Premium Shop",
                    "menu_subtitle": "Produtos ilimitados e funcoes.",
                    "hero_subheading": "Produtos ilimitados e todas as funcoes.",
                    "main_body": "Ecommerce completo com todas as funcoes.",
                },
            },
            "websites-custom": {
                "en": {
                    "title": "Custom Websites",
                    "nav_label": "Custom",
                    "menu_subtitle": "Built to your requirements.",
                    "hero_subheading": "Custom builds tailored to your requirements.",
                    "main_body": "Custom layouts, integrations, and unique workflows.",
                },
                "nl": {
                    "title": "Custom websites",
                    "nav_label": "Custom",
                    "menu_subtitle": "Gebouwd op jouw eisen.",
                    "hero_subheading": "Custom builds afgestemd op jouw eisen.",
                    "main_body": "Custom layouts, integraties en unieke flows.",
                },
                "fr": {
                    "title": "Sites sur mesure",
                    "nav_label": "Custom",
                    "menu_subtitle": "Construit selon vos besoins.",
                    "hero_subheading": "Sites sur mesure adaptes a vos besoins.",
                    "main_body": "Layouts sur mesure, integrations et workflows.",
                },
                "de": {
                    "title": "Custom Websites",
                    "nav_label": "Custom",
                    "menu_subtitle": "Nach Ihren Anforderungen gebaut.",
                    "hero_subheading": "Individuelle Builds nach Ihren Anforderungen.",
                    "main_body": "Individuelle Layouts, Integrationen und Workflows.",
                },
                "es": {
                    "title": "Websites a medida",
                    "nav_label": "Custom",
                    "menu_subtitle": "Construido a tus requisitos.",
                    "hero_subheading": "Webs a medida segun tus requisitos.",
                    "main_body": "Layouts personalizados e integraciones.",
                },
                "pt": {
                    "title": "Websites personalizados",
                    "nav_label": "Custom",
                    "menu_subtitle": "Construido a sua medida.",
                    "hero_subheading": "Sites personalizados para os seus requisitos.",
                    "main_body": "Layouts personalizados e integracoes.",
                },
            },
        }

        printlab_pages = {
            "printlab": {
                "en": {
                    "title": "PrintLab",
                    "nav_label": "PrintLab",
                    "menu_subtitle": "Design and prepare your printed materials online. Upload your designs, preview your products, and get everything ready for print. Orders can be completed later, with no payment required to start.",
                    "hero_subheading": "Design and prepare your printed materials online. Upload your designs, preview your products, and get everything ready for print. Orders can be completed later, with no payment required to start.",
                    "main_body": "PrintLab helps you turn your brand into real, physical products. From business cards to clothing and merchandise, everything starts with your design. You can upload your files directly from your computer, preview how they look, and keep them ready for print. This makes it easy to prepare professional materials without technical steps or back and forth. Business cards and paper products: Create professional paper products that represent your business clearly. Design and upload business cards, flyers, brochures, and similar materials. Choose layouts that fit your brand and preview the final result. Perfect for local businesses, events, and everyday use. Common items include business cards, flyers and brochures, trifolds and handouts, and other print-ready paper materials. Clothing for your brand: Add your logo or design to clothing items for your business or team. This includes options for men, women, and children. Upload your design and see how it looks on different products. Ideal for workwear, promotions, and branded apparel. Typical options include T-shirts, hoodies, workwear, and multiple sizes and fits. Merchandise and gifts: Create branded merchandise and gifts for customers or promotions. From mugs to bags and accessories, PrintLab helps you prepare designs easily. These products are great for giveaways, promotions, or online branding. All designs can be uploaded and previewed before ordering. Popular items include mugs and drinkware, bags and accessories, and promotional items. More print options: PrintLab supports a wide range of additional products. If it can be printed, it can usually be prepared here. Upload your design, preview the product, and keep it ready for production. More product types can be added over time. How PrintLab works: 1) Choose a product type. 2) Upload your design from your computer. 3) Preview how it looks. 4) Submit your print request. Orders and payments can be completed later. You stay in control. Start designing your print materials. Upload your designs and prepare everything for print, with no payment required to begin.",
                },
                "nl": {
                    "title": "PrintLab",
                    "nav_label": "PrintLab",
                    "menu_subtitle": "Design and prepare your printed materials online. Upload your designs, preview your products, and get everything ready for print. Orders can be completed later, with no payment required to start.",
                    "hero_subheading": "Design and prepare your printed materials online. Upload your designs, preview your products, and get everything ready for print. Orders can be completed later, with no payment required to start.",
                    "main_body": "PrintLab helps you turn your brand into real, physical products. From business cards to clothing and merchandise, everything starts with your design. You can upload your files directly from your computer, preview how they look, and keep them ready for print. This makes it easy to prepare professional materials without technical steps or back and forth. Business cards and paper products: Create professional paper products that represent your business clearly. Design and upload business cards, flyers, brochures, and similar materials. Choose layouts that fit your brand and preview the final result. Perfect for local businesses, events, and everyday use. Common items include business cards, flyers and brochures, trifolds and handouts, and other print-ready paper materials. Clothing for your brand: Add your logo or design to clothing items for your business or team. This includes options for men, women, and children. Upload your design and see how it looks on different products. Ideal for workwear, promotions, and branded apparel. Typical options include T-shirts, hoodies, workwear, and multiple sizes and fits. Merchandise and gifts: Create branded merchandise and gifts for customers or promotions. From mugs to bags and accessories, PrintLab helps you prepare designs easily. These products are great for giveaways, promotions, or online branding. All designs can be uploaded and previewed before ordering. Popular items include mugs and drinkware, bags and accessories, and promotional items. More print options: PrintLab supports a wide range of additional products. If it can be printed, it can usually be prepared here. Upload your design, preview the product, and keep it ready for production. More product types can be added over time. How PrintLab works: 1) Choose a product type. 2) Upload your design from your computer. 3) Preview how it looks. 4) Submit your print request. Orders and payments can be completed later. You stay in control. Start designing your print materials. Upload your designs and prepare everything for print, with no payment required to begin.",
                },
                "fr": {
                    "title": "PrintLab",
                    "nav_label": "PrintLab",
                    "menu_subtitle": "Design and prepare your printed materials online. Upload your designs, preview your products, and get everything ready for print. Orders can be completed later, with no payment required to start.",
                    "hero_subheading": "Design and prepare your printed materials online. Upload your designs, preview your products, and get everything ready for print. Orders can be completed later, with no payment required to start.",
                    "main_body": "PrintLab helps you turn your brand into real, physical products. From business cards to clothing and merchandise, everything starts with your design. You can upload your files directly from your computer, preview how they look, and keep them ready for print. This makes it easy to prepare professional materials without technical steps or back and forth. Business cards and paper products: Create professional paper products that represent your business clearly. Design and upload business cards, flyers, brochures, and similar materials. Choose layouts that fit your brand and preview the final result. Perfect for local businesses, events, and everyday use. Common items include business cards, flyers and brochures, trifolds and handouts, and other print-ready paper materials. Clothing for your brand: Add your logo or design to clothing items for your business or team. This includes options for men, women, and children. Upload your design and see how it looks on different products. Ideal for workwear, promotions, and branded apparel. Typical options include T-shirts, hoodies, workwear, and multiple sizes and fits. Merchandise and gifts: Create branded merchandise and gifts for customers or promotions. From mugs to bags and accessories, PrintLab helps you prepare designs easily. These products are great for giveaways, promotions, or online branding. All designs can be uploaded and previewed before ordering. Popular items include mugs and drinkware, bags and accessories, and promotional items. More print options: PrintLab supports a wide range of additional products. If it can be printed, it can usually be prepared here. Upload your design, preview the product, and keep it ready for production. More product types can be added over time. How PrintLab works: 1) Choose a product type. 2) Upload your design from your computer. 3) Preview how it looks. 4) Submit your print request. Orders and payments can be completed later. You stay in control. Start designing your print materials. Upload your designs and prepare everything for print, with no payment required to begin.",
                },
                "de": {
                    "title": "PrintLab",
                    "nav_label": "PrintLab",
                    "menu_subtitle": "White Label Druck via Printful spaeter.",
                    "hero_subheading": "Design and prepare your printed materials online. Upload your designs, preview your products, and get everything ready for print. Orders can be completed later, with no payment required to start.",
                    "main_body": "PrintLab helps you turn your brand into real, physical products. From business cards to clothing and merchandise, everything starts with your design. You can upload your files directly from your computer, preview how they look, and keep them ready for print. This makes it easy to prepare professional materials without technical steps or back and forth. Business cards and paper products: Create professional paper products that represent your business clearly. Design and upload business cards, flyers, brochures, and similar materials. Choose layouts that fit your brand and preview the final result. Perfect for local businesses, events, and everyday use. Common items include business cards, flyers and brochures, trifolds and handouts, and other print-ready paper materials. Clothing for your brand: Add your logo or design to clothing items for your business or team. This includes options for men, women, and children. Upload your design and see how it looks on different products. Ideal for workwear, promotions, and branded apparel. Typical options include T-shirts, hoodies, workwear, and multiple sizes and fits. Merchandise and gifts: Create branded merchandise and gifts for customers or promotions. From mugs to bags and accessories, PrintLab helps you prepare designs easily. These products are great for giveaways, promotions, or online branding. All designs can be uploaded and previewed before ordering. Popular items include mugs and drinkware, bags and accessories, and promotional items. More print options: PrintLab supports a wide range of additional products. If it can be printed, it can usually be prepared here. Upload your design, preview the product, and keep it ready for production. More product types can be added over time. How PrintLab works: 1) Choose a product type. 2) Upload your design from your computer. 3) Preview how it looks. 4) Submit your print request. Orders and payments can be completed later. You stay in control. Start designing your print materials. Upload your designs and prepare everything for print, with no payment required to begin.",
                },
                "es": {
                    "title": "PrintLab",
                    "nav_label": "PrintLab",
                    "menu_subtitle": "Print white label via Printful mas adelante.",
                    "hero_subheading": "Design and prepare your printed materials online. Upload your designs, preview your products, and get everything ready for print. Orders can be completed later, with no payment required to start.",
                    "main_body": "PrintLab helps you turn your brand into real, physical products. From business cards to clothing and merchandise, everything starts with your design. You can upload your files directly from your computer, preview how they look, and keep them ready for print. This makes it easy to prepare professional materials without technical steps or back and forth. Business cards and paper products: Create professional paper products that represent your business clearly. Design and upload business cards, flyers, brochures, and similar materials. Choose layouts that fit your brand and preview the final result. Perfect for local businesses, events, and everyday use. Common items include business cards, flyers and brochures, trifolds and handouts, and other print-ready paper materials. Clothing for your brand: Add your logo or design to clothing items for your business or team. This includes options for men, women, and children. Upload your design and see how it looks on different products. Ideal for workwear, promotions, and branded apparel. Typical options include T-shirts, hoodies, workwear, and multiple sizes and fits. Merchandise and gifts: Create branded merchandise and gifts for customers or promotions. From mugs to bags and accessories, PrintLab helps you prepare designs easily. These products are great for giveaways, promotions, or online branding. All designs can be uploaded and previewed before ordering. Popular items include mugs and drinkware, bags and accessories, and promotional items. More print options: PrintLab supports a wide range of additional products. If it can be printed, it can usually be prepared here. Upload your design, preview the product, and keep it ready for production. More product types can be added over time. How PrintLab works: 1) Choose a product type. 2) Upload your design from your computer. 3) Preview how it looks. 4) Submit your print request. Orders and payments can be completed later. You stay in control. Start designing your print materials. Upload your designs and prepare everything for print, with no payment required to begin.",
                },
                "pt": {
                    "title": "PrintLab",
                    "nav_label": "PrintLab",
                    "menu_subtitle": "Print white label via Printful mais tarde.",
                    "hero_subheading": "Design and prepare your printed materials online. Upload your designs, preview your products, and get everything ready for print. Orders can be completed later, with no payment required to start.",
                    "main_body": "PrintLab helps you turn your brand into real, physical products. From business cards to clothing and merchandise, everything starts with your design. You can upload your files directly from your computer, preview how they look, and keep them ready for print. This makes it easy to prepare professional materials without technical steps or back and forth. Business cards and paper products: Create professional paper products that represent your business clearly. Design and upload business cards, flyers, brochures, and similar materials. Choose layouts that fit your brand and preview the final result. Perfect for local businesses, events, and everyday use. Common items include business cards, flyers and brochures, trifolds and handouts, and other print-ready paper materials. Clothing for your brand: Add your logo or design to clothing items for your business or team. This includes options for men, women, and children. Upload your design and see how it looks on different products. Ideal for workwear, promotions, and branded apparel. Typical options include T-shirts, hoodies, workwear, and multiple sizes and fits. Merchandise and gifts: Create branded merchandise and gifts for customers or promotions. From mugs to bags and accessories, PrintLab helps you prepare designs easily. These products are great for giveaways, promotions, or online branding. All designs can be uploaded and previewed before ordering. Popular items include mugs and drinkware, bags and accessories, and promotional items. More print options: PrintLab supports a wide range of additional products. If it can be printed, it can usually be prepared here. Upload your design, preview the product, and keep it ready for production. More product types can be added over time. How PrintLab works: 1) Choose a product type. 2) Upload your design from your computer. 3) Preview how it looks. 4) Submit your print request. Orders and payments can be completed later. You stay in control. Start designing your print materials. Upload your designs and prepare everything for print, with no payment required to begin.",
                },
            },
            "printlab-business-cards": {
                "en": {
                    "title": "Business Cards",
                    "nav_label": "Business Cards",
                    "menu_subtitle": "Classic cards, Printful fulfillment later.",
                    "hero_subheading": "Business cards fulfilled by Printful later.",
                    "main_body": "White-label cards with fulfillment later by Printful.",
                },
                "nl": {
                    "title": "Visitekaartjes",
                    "nav_label": "Visitekaartjes",
                    "menu_subtitle": "Kaarten via Printful later.",
                    "hero_subheading": "Kaarten via Printful later.",
                    "main_body": "White-label kaarten met Printful later.",
                },
                "fr": {
                    "title": "Cartes de visite",
                    "nav_label": "Cartes",
                    "menu_subtitle": "Cartes via Printful plus tard.",
                    "hero_subheading": "Cartes via Printful plus tard.",
                    "main_body": "Cartes white label via Printful plus tard.",
                },
                "de": {
                    "title": "Visitenkarten",
                    "nav_label": "Visitenkarten",
                    "menu_subtitle": "Karten via Printful spaeter.",
                    "hero_subheading": "Karten via Printful spaeter.",
                    "main_body": "White Label Karten via Printful spaeter.",
                },
                "es": {
                    "title": "Tarjetas",
                    "nav_label": "Tarjetas",
                    "menu_subtitle": "Tarjetas via Printful mas adelante.",
                    "hero_subheading": "Tarjetas via Printful mas adelante.",
                    "main_body": "Tarjetas white label via Printful mas adelante.",
                },
                "pt": {
                    "title": "Cartoes",
                    "nav_label": "Cartoes",
                    "menu_subtitle": "Cartoes via Printful mais tarde.",
                    "hero_subheading": "Cartoes via Printful mais tarde.",
                    "main_body": "Cartoes white label via Printful mais tarde.",
                },
            },
            "printlab-flyers": {
                "en": {
                    "title": "Flyers",
                    "nav_label": "Flyers",
                    "menu_subtitle": "Flyers via Printful later.",
                    "hero_subheading": "Flyers fulfilled by Printful later.",
                    "main_body": "White-label flyers with fulfillment later by Printful.",
                },
                "nl": {
                    "title": "Flyers",
                    "nav_label": "Flyers",
                    "menu_subtitle": "Flyers via Printful later.",
                    "hero_subheading": "Flyers via Printful later.",
                    "main_body": "White-label flyers via Printful later.",
                },
                "fr": {
                    "title": "Flyers",
                    "nav_label": "Flyers",
                    "menu_subtitle": "Flyers via Printful plus tard.",
                    "hero_subheading": "Flyers via Printful plus tard.",
                    "main_body": "Flyers white label via Printful plus tard.",
                },
                "de": {
                    "title": "Flyer",
                    "nav_label": "Flyer",
                    "menu_subtitle": "Flyer via Printful spaeter.",
                    "hero_subheading": "Flyer via Printful spaeter.",
                    "main_body": "White Label Flyer via Printful spaeter.",
                },
                "es": {
                    "title": "Flyers",
                    "nav_label": "Flyers",
                    "menu_subtitle": "Flyers via Printful mas adelante.",
                    "hero_subheading": "Flyers via Printful mas adelante.",
                    "main_body": "Flyers white label via Printful mas adelante.",
                },
                "pt": {
                    "title": "Flyers",
                    "nav_label": "Flyers",
                    "menu_subtitle": "Flyers via Printful mais tarde.",
                    "hero_subheading": "Flyers via Printful mais tarde.",
                    "main_body": "Flyers white label via Printful mais tarde.",
                },
            },
            "printlab-brochures": {
                "en": {
                    "title": "Brochures",
                    "nav_label": "Brochures",
                    "menu_subtitle": "Brochures via Printful later.",
                    "hero_subheading": "Brochures fulfilled by Printful later.",
                    "main_body": "White-label brochures with fulfillment later by Printful.",
                },
                "nl": {
                    "title": "Brochures",
                    "nav_label": "Brochures",
                    "menu_subtitle": "Brochures via Printful later.",
                    "hero_subheading": "Brochures via Printful later.",
                    "main_body": "White-label brochures via Printful later.",
                },
                "fr": {
                    "title": "Brochures",
                    "nav_label": "Brochures",
                    "menu_subtitle": "Brochures via Printful plus tard.",
                    "hero_subheading": "Brochures via Printful plus tard.",
                    "main_body": "Brochures white label via Printful plus tard.",
                },
                "de": {
                    "title": "Broschueren",
                    "nav_label": "Broschueren",
                    "menu_subtitle": "Broschueren via Printful spaeter.",
                    "hero_subheading": "Broschueren via Printful spaeter.",
                    "main_body": "White Label Broschueren via Printful spaeter.",
                },
                "es": {
                    "title": "Brochures",
                    "nav_label": "Brochures",
                    "menu_subtitle": "Brochures via Printful mas adelante.",
                    "hero_subheading": "Brochures via Printful mas adelante.",
                    "main_body": "Brochures white label via Printful mas adelante.",
                },
                "pt": {
                    "title": "Brochures",
                    "nav_label": "Brochures",
                    "menu_subtitle": "Brochures via Printful mais tarde.",
                    "hero_subheading": "Brochures via Printful mais tarde.",
                    "main_body": "Brochures white label via Printful mais tarde.",
                },
            },
            "printlab-stickers": {
                "en": {
                    "title": "Stickers",
                    "nav_label": "Stickers",
                    "menu_subtitle": "Stickers via Printful later.",
                    "hero_subheading": "Stickers fulfilled by Printful later.",
                    "main_body": "White-label stickers with fulfillment later by Printful.",
                },
                "nl": {
                    "title": "Stickers",
                    "nav_label": "Stickers",
                    "menu_subtitle": "Stickers via Printful later.",
                    "hero_subheading": "Stickers via Printful later.",
                    "main_body": "White-label stickers via Printful later.",
                },
                "fr": {
                    "title": "Stickers",
                    "nav_label": "Stickers",
                    "menu_subtitle": "Stickers via Printful plus tard.",
                    "hero_subheading": "Stickers via Printful plus tard.",
                    "main_body": "Stickers white label via Printful plus tard.",
                },
                "de": {
                    "title": "Sticker",
                    "nav_label": "Sticker",
                    "menu_subtitle": "Sticker via Printful spaeter.",
                    "hero_subheading": "Sticker via Printful spaeter.",
                    "main_body": "White Label Sticker via Printful spaeter.",
                },
                "es": {
                    "title": "Stickers",
                    "nav_label": "Stickers",
                    "menu_subtitle": "Stickers via Printful mas adelante.",
                    "hero_subheading": "Stickers via Printful mas adelante.",
                    "main_body": "Stickers white label via Printful mas adelante.",
                },
                "pt": {
                    "title": "Stickers",
                    "nav_label": "Stickers",
                    "menu_subtitle": "Stickers via Printful mais tarde.",
                    "hero_subheading": "Stickers via Printful mais tarde.",
                    "main_body": "Stickers white label via Printful mais tarde.",
                },
            },
            "printlab-apparel": {
                "en": {
                    "title": "Apparel",
                    "nav_label": "Apparel",
                    "menu_subtitle": "Apparel via Printful later.",
                    "hero_subheading": "Apparel fulfilled by Printful later.",
                    "main_body": "White-label apparel with fulfillment later by Printful.",
                },
                "nl": {
                    "title": "Apparel",
                    "nav_label": "Apparel",
                    "menu_subtitle": "Apparel via Printful later.",
                    "hero_subheading": "Apparel via Printful later.",
                    "main_body": "White-label apparel via Printful later.",
                },
                "fr": {
                    "title": "Apparel",
                    "nav_label": "Apparel",
                    "menu_subtitle": "Apparel via Printful plus tard.",
                    "hero_subheading": "Apparel via Printful plus tard.",
                    "main_body": "Apparel white label via Printful plus tard.",
                },
                "de": {
                    "title": "Apparel",
                    "nav_label": "Apparel",
                    "menu_subtitle": "Apparel via Printful spaeter.",
                    "hero_subheading": "Apparel via Printful spaeter.",
                    "main_body": "White Label Apparel via Printful spaeter.",
                },
                "es": {
                    "title": "Apparel",
                    "nav_label": "Apparel",
                    "menu_subtitle": "Apparel via Printful mas adelante.",
                    "hero_subheading": "Apparel via Printful mas adelante.",
                    "main_body": "Apparel white label via Printful mas adelante.",
                },
                "pt": {
                    "title": "Apparel",
                    "nav_label": "Apparel",
                    "menu_subtitle": "Apparel via Printful mais tarde.",
                    "hero_subheading": "Apparel via Printful mais tarde.",
                    "main_body": "Apparel white label via Printful mais tarde.",
                },
            },
            "printlab-merch": {
                "en": {
                    "title": "Merch",
                    "nav_label": "Merch",
                    "menu_subtitle": "Merch via Printful later.",
                    "hero_subheading": "Merch fulfilled by Printful later.",
                    "main_body": "White-label merch with fulfillment later by Printful.",
                },
                "nl": {
                    "title": "Merch",
                    "nav_label": "Merch",
                    "menu_subtitle": "Merch via Printful later.",
                    "hero_subheading": "Merch via Printful later.",
                    "main_body": "White-label merch via Printful later.",
                },
                "fr": {
                    "title": "Merch",
                    "nav_label": "Merch",
                    "menu_subtitle": "Merch via Printful plus tard.",
                    "hero_subheading": "Merch via Printful plus tard.",
                    "main_body": "Merch white label via Printful plus tard.",
                },
                "de": {
                    "title": "Merch",
                    "nav_label": "Merch",
                    "menu_subtitle": "Merch via Printful spaeter.",
                    "hero_subheading": "Merch via Printful spaeter.",
                    "main_body": "White Label Merch via Printful spaeter.",
                },
                "es": {
                    "title": "Merch",
                    "nav_label": "Merch",
                    "menu_subtitle": "Merch via Printful mas adelante.",
                    "hero_subheading": "Merch via Printful mas adelante.",
                    "main_body": "Merch white label via Printful mas adelante.",
                },
                "pt": {
                    "title": "Merch",
                    "nav_label": "Merch",
                    "menu_subtitle": "Merch via Printful mais tarde.",
                    "hero_subheading": "Merch via Printful mais tarde.",
                    "main_body": "Merch white label via Printful mais tarde.",
                },
            },
        }

        websites_defaults = {
            "en": {"cta_primary": "Start now", "cta_secondary": "See plans"},
            "nl": {"cta_primary": "Start nu", "cta_secondary": "Bekijk plannen"},
            "fr": {"cta_primary": "Demarrer", "cta_secondary": "Voir les offres"},
            "de": {"cta_primary": "Jetzt starten", "cta_secondary": "Plaene ansehen"},
            "es": {"cta_primary": "Empezar", "cta_secondary": "Ver planes"},
            "pt": {"cta_primary": "Comecar", "cta_secondary": "Ver planos"},
        }

        printlab_defaults = {
            "en": {"cta_primary": "Start print", "cta_secondary": "See categories"},
            "nl": {"cta_primary": "Start print", "cta_secondary": "Bekijk categorieen"},
            "fr": {"cta_primary": "Demarrer print", "cta_secondary": "Voir categories"},
            "de": {"cta_primary": "Druck starten", "cta_secondary": "Kategorien ansehen"},
            "es": {"cta_primary": "Empezar print", "cta_secondary": "Ver categorias"},
            "pt": {"cta_primary": "Comecar print", "cta_secondary": "Ver categorias"},
        }

        overview_titles = {
            "en": "Overview",
            "nl": "Overzicht",
            "fr": "Apercu",
            "de": "Uebersicht",
            "es": "Resumen",
            "pt": "Resumo",
        }

        for slug, translations in websites_plan_pages.items():
            page_translations[slug] = {}
            for lang in languages:
                info = translations[lang]
                defaults = websites_defaults[lang]
                overview_title = overview_titles[lang]
                page_translations[slug][lang] = {
                    "title": info["title"],
                    "nav_label": info["nav_label"],
                    "menu_subtitle": info["menu_subtitle"],
                    "meta_title": info["title"],
                    "meta_description": info["main_body"],
                    "hero": {
                        "heading": info["title"],
                        "subheading": info["hero_subheading"],
                        "cta_primary_text": defaults["cta_primary"],
                        "cta_secondary_text": defaults["cta_secondary"],
                    },
                    "main": {"heading": overview_title, "body": info["main_body"]},
                    "cta": {"cta_primary_text": defaults["cta_primary"]},
                }

        for slug, translations in printlab_pages.items():
            page_translations[slug] = {}
            for lang in languages:
                info = translations[lang]
                defaults = printlab_defaults[lang]
                overview_title = overview_titles[lang]
                page_translations[slug][lang] = {
                    "title": info["title"],
                    "nav_label": info["nav_label"],
                    "menu_subtitle": info["menu_subtitle"],
                    "meta_title": info["title"],
                    "meta_description": info["main_body"],
                    "hero": {
                        "heading": info["title"],
                        "subheading": info["hero_subheading"],
                        "cta_primary_text": defaults["cta_primary"],
                        "cta_secondary_text": defaults["cta_secondary"],
                    },
                    "main": {"heading": overview_title, "body": info["main_body"]},
                    "cta": {"cta_primary_text": defaults["cta_primary"]},
                }

        def ensure_section(page_obj, key, order):
            section, _ = PageSection.objects.get_or_create(
                page=page_obj,
                key=key,
                defaults={"order": order, "is_visible": True},
            )
            if section.order != order:
                section.order = order
                section.save(update_fields=["order"])
            content, _ = SectionContent.objects.get_or_create(section=section)
            return content

        for slug, translations in page_translations.items():
            page_obj, _ = Page.objects.get_or_create(
                slug=slug,
                defaults={"is_active": True, "template_key": slug},
            )
            for lang in languages:
                data = translations[lang]
                page_obj.set_current_language(lang)
                page_obj.title = data["title"]
                page_obj.nav_label = data.get("nav_label", "")
                page_obj.menu_subtitle = data.get("menu_subtitle", "")
                page_obj.meta_title = data["meta_title"]
                page_obj.meta_description = data["meta_description"]
                page_obj.meta_robots_index = True
                page_obj.meta_robots_follow = True
                page_obj.save()

            hero_content = ensure_section(page_obj, "hero", 1)
            main_content = ensure_section(page_obj, "main", 2)
            cta_content = ensure_section(page_obj, "cta", 3)
            policy_content = None
            disclosure_content = None
            affiliate_contents = []
            pos_category_contents = []
            faq_contents = []
            next_order = 4
            if "pos_category_cards" in translations.get("en", {}):
                for idx, _ in enumerate(
                    translations["en"]["pos_category_cards"], start=1
                ):
                    pos_category_contents.append(
                        ensure_section(page_obj, f"pos_category_card_{idx}", next_order)
                    )
                    next_order += 1
            if "policy_notice" in translations.get("en", {}):
                policy_content = ensure_section(
                    page_obj, "printful_policy_notice", next_order
                )
                next_order += 1
            if "affiliate_disclosure" in translations.get("en", {}):
                disclosure_content = ensure_section(
                    page_obj, "affiliate_disclosure", next_order
                )
                next_order += 1
            if "affiliate_blocks" in translations.get("en", {}):
                for idx, _ in enumerate(translations["en"]["affiliate_blocks"], start=1):
                    affiliate_contents.append(
                        ensure_section(
                            page_obj, f"pos_affiliate_block_{idx}", next_order
                        )
                    )
                    next_order += 1
            if "faq_items" in translations.get("en", {}):
                for idx, _ in enumerate(translations["en"]["faq_items"], start=1):
                    faq_contents.append(
                        ensure_section(page_obj, f"faq_{idx}", next_order)
                    )
                    next_order += 1

            for lang in languages:
                data = translations[lang]

                hero_content.set_current_language(lang)
                hero_content.heading = data["hero"]["heading"]
                hero_content.subheading = data["hero"]["subheading"]
                hero_content.cta_primary_text = data["hero"]["cta_primary_text"]
                hero_content.cta_secondary_text = data["hero"]["cta_secondary_text"]
                hero_content.save()

                main_content.set_current_language(lang)
                main_content.heading = data["main"]["heading"]
                main_content.body = data["main"]["body"]
                main_content.save()

                cta_content.set_current_language(lang)
                cta_content.heading = data["cta"].get("heading", "")
                cta_content.body = data["cta"].get("body", "")
                cta_content.cta_primary_text = data["cta"]["cta_primary_text"]
                cta_content.cta_primary_url = data["cta"].get("cta_primary_url", "")
                cta_content.save()

                if policy_content and "policy_notice" in data:
                    policy_content.set_current_language(lang)
                    policy_content.heading = data["policy_notice"]["heading"]
                    policy_content.body = data["policy_notice"]["body"]
                    policy_content.cta_primary_text = data["policy_notice"]["cta_primary_text"]
                    policy_content.cta_primary_url = data["policy_notice"]["cta_primary_url"]
                    policy_content.save()

                if disclosure_content and "affiliate_disclosure" in data:
                    disclosure_content.set_current_language(lang)
                    disclosure_content.body = data["affiliate_disclosure"]["body"]
                    disclosure_content.save()

                if affiliate_contents and "affiliate_blocks" in data:
                    for idx, block in enumerate(data["affiliate_blocks"]):
                        if idx >= len(affiliate_contents):
                            break
                        block_content = affiliate_contents[idx]
                        block_content.set_current_language(lang)
                        block_content.heading = block.get("heading", "")
                        block_content.subheading = block.get("subheading", "")
                        block_content.body = block.get("body", "")
                        block_content.cta_primary_text = block.get(
                            "cta_primary_text", ""
                        )
                        block_content.cta_primary_url = block.get("cta_primary_url", "")
                        block_content.cta_secondary_text = block.get(
                            "cta_secondary_text", ""
                        )
                        block_content.cta_secondary_url = block.get(
                            "cta_secondary_url", ""
                        )
                        block_content.save()

                if pos_category_contents and "pos_category_cards" in data:
                    for idx, card in enumerate(data["pos_category_cards"]):
                        if idx >= len(pos_category_contents):
                            break
                        card_content = pos_category_contents[idx]
                        card_content.set_current_language(lang)
                        card_content.heading = card.get("heading", "")
                        card_content.subheading = card.get("subheading", "")
                        bullets = card.get("bullets", [])
                        card_content.body = "".join(f"<li>{item}</li>" for item in bullets)
                        card_content.cta_primary_text = card.get(
                            "cta_primary_text", ""
                        )
                        card_content.cta_primary_url = card.get(
                            "cta_primary_url", ""
                        )
                        card_content.save()

                if faq_contents and "faq_items" in data:
                    for idx, item in enumerate(data["faq_items"]):
                        if idx >= len(faq_contents):
                            break
                        faq_content = faq_contents[idx]
                        faq_content.set_current_language(lang)
                        faq_content.heading = item.get("heading", "")
                        faq_content.body = item.get("body", "")
                        faq_content.save()

        feature, _ = Feature.objects.get_or_create(
            key="particles_hero",
            defaults={
                "name": "Particles Hero",
                "description": "Particles background for the homepage hero.",
                "is_enabled": False,
                "is_paid": True,
            },
        )
        if feature.name != "Particles Hero":
            feature.name = "Particles Hero"
            feature.save(update_fields=["name"])

        print_studio_feature, _ = Feature.objects.get_or_create(
            key="print_studio",
            defaults={
                "name": "Print Studio",
                "description": "Printful API integration and uploads will be added in a later phase.",
                "is_enabled": True,
                "is_paid": True,
            },
        )
        if print_studio_feature.name != "Print Studio":
            print_studio_feature.name = "Print Studio"
            print_studio_feature.save(update_fields=["name"])

        pos_affiliates_feature, _ = Feature.objects.get_or_create(
            key="pos_affiliates",
            defaults={
                "name": "Card Payments",
                "description": "Affiliate-driven POS comparisons and information.",
                "is_enabled": True,
                "is_paid": False,
            },
        )
        if pos_affiliates_feature.name != "Card Payments":
            pos_affiliates_feature.name = "Card Payments"
            pos_affiliates_feature.save(update_fields=["name"])

        HeroParticlesSettings.objects.get_or_create(
            feature=feature,
            defaults={"apply_to": "home", "is_enabled": False},
        )

        plan_translations = {
            "starter": {
                "en": ("Starter", "Best for small local businesses", "EUR 19 / month"),
                "nl": ("Starter", "Voor kleine lokale bedrijven", "EUR 19 / maand"),
                "fr": ("Starter", "Pour petites entreprises locales", "EUR 19 / mois"),
                "de": ("Starter", "Fuer kleine lokale Betriebe", "EUR 19 / Monat"),
                "es": ("Starter", "Para negocios locales pequenos", "EUR 19 / mes"),
                "pt": ("Starter", "Para negocios locais pequenos", "EUR 19 / mes"),
            },
            "growth": {
                "en": ("Growth", "For growing teams and services", "EUR 39 / month"),
                "nl": ("Growth", "Voor groeiende teams en diensten", "EUR 39 / maand"),
                "fr": ("Growth", "Pour equipes en croissance", "EUR 39 / mois"),
                "de": ("Growth", "Fuer wachsende Teams", "EUR 39 / Monat"),
                "es": ("Growth", "Para equipos en crecimiento", "EUR 39 / mes"),
                "pt": ("Growth", "Para equipas em crescimento", "EUR 39 / mes"),
            },
            "pro": {
                "en": ("Pro", "Advanced tools and priority support", "EUR 69 / month"),
                "nl": ("Pro", "Geavanceerde tools en prioriteit support", "EUR 69 / maand"),
                "fr": ("Pro", "Outils avances et support prioritaire", "EUR 69 / mois"),
                "de": ("Pro", "Erweiterte Tools und Prioritat Support", "EUR 69 / Monat"),
                "es": ("Pro", "Herramientas avanzadas y soporte prioritario", "EUR 69 / mes"),
                "pt": ("Pro", "Ferramentas avancadas e suporte prioritario", "EUR 69 / mes"),
            },
        }

        plan_order = {"starter": 1, "growth": 2, "pro": 3}
        for plan_key, translations in plan_translations.items():
            plan, _ = Plan.objects.get_or_create(
                key=plan_key,
                defaults={
                    "is_active": True,
                    "sort_order": plan_order.get(plan_key, 0),
                    "slug": plan_key,
                },
            )
            plan.set_current_language("en")
            plan.name = plan_key.title()
            plan.save()
            if plan.sort_order != plan_order.get(plan_key, 0):
                plan.sort_order = plan_order.get(plan_key, 0)
                plan.save(update_fields=["sort_order"])
            for lang in languages:
                name, description, price_display = translations[lang]
                plan.set_current_language(lang)
                plan.name = name
                plan.description = description
                plan.price_display = price_display
                plan.save()

        plan_feature_map = {
            "starter": ["pos_affiliates"],
            "growth": ["particles_hero", "print_studio", "pos_affiliates"],
            "pro": ["particles_hero", "print_studio", "pos_affiliates"],
        }
        for plan_key, feature_keys in plan_feature_map.items():
            plan = Plan.objects.filter(key=plan_key).first()
            if not plan:
                continue
            for feature_key in feature_keys:
                feat = Feature.objects.filter(key=feature_key).first()
                if not feat:
                    continue
                PlanFeature.objects.get_or_create(
                    plan=plan,
                    feature=feat,
                    defaults={"is_enabled": True},
                )

        default_panel, _ = RightSidebarPanel.objects.get_or_create(
            page=None,
            defaults={
                "is_enabled": True,
                "phone": "+31 20 123 4567",
                "email": "hello@justcodeworks.eu",
                "address": "Amsterdam, Netherlands",
                "maps_url": "https://maps.google.com",
                "cta_url": "/contact/",
                "show_social": True,
            },
        )

        default_translations = {
            "en": {
                "headline": "Talk to JustCodeWorks",
                "intro": "Questions about websites, print, or POS? We reply fast.",
                "cta_text": "Start a project",
                "extra_html": "<ul><li>Fast onboarding</li><li>EU-first hosting</li><li>Clear monthly pricing</li></ul>",
            },
            "nl": {
                "headline": "Praat met JustCodeWorks",
                "intro": "Vragen over websites, print of POS? We reageren snel.",
                "cta_text": "Start een project",
                "extra_html": "<ul><li>Snelle start</li><li>EU hosting</li><li>Heldere prijzen</li></ul>",
            },
            "fr": {
                "headline": "Parlez a JustCodeWorks",
                "intro": "Des questions sur sites, print ou POS? Reponse rapide.",
                "cta_text": "Demarrer un projet",
                "extra_html": "<ul><li>Demarrage rapide</li><li>Hebergement UE</li><li>Prix clairs</li></ul>",
            },
            "de": {
                "headline": "Sprechen Sie mit JustCodeWorks",
                "intro": "Fragen zu Websites, Druck oder POS? Schnell antworten.",
                "cta_text": "Projekt starten",
                "extra_html": "<ul><li>Schneller Start</li><li>EU Hosting</li><li>Klare Preise</li></ul>",
            },
            "es": {
                "headline": "Hable con JustCodeWorks",
                "intro": "Dudas sobre web, impresion o POS? Respondemos rapido.",
                "cta_text": "Iniciar proyecto",
                "extra_html": "<ul><li>Inicio rapido</li><li>Hosting UE</li><li>Precios claros</li></ul>",
            },
            "pt": {
                "headline": "Fale com a JustCodeWorks",
                "intro": "Duvidas sobre sites, print ou POS? Resposta rapida.",
                "cta_text": "Iniciar projeto",
                "extra_html": "<ul><li>Arranque rapido</li><li>Hosting UE</li><li>Precos claros</li></ul>",
            },
        }

        for lang in languages:
            data = default_translations[lang]
            default_panel.set_current_language(lang)
            default_panel.headline = data["headline"]
            default_panel.intro = data["intro"]
            default_panel.cta_text = data["cta_text"]
            default_panel.extra_html = data["extra_html"]
            default_panel.save()

        page_sidebar_copy = {
            "home": {
                "en": ("Get started today", "Launch your online presence with one simple setup."),
                "nl": ("Start vandaag", "Zet je online aanwezigheid snel live."),
                "fr": ("Commencez aujourd'hui", "Lancez votre presence en ligne simplement."),
                "de": ("Heute starten", "Bringen Sie Ihre Online-Prasenz schnell live."),
                "es": ("Empieza hoy", "Lanza tu presencia online sin complicaciones."),
                "pt": ("Comece hoje", "Coloque a sua presenca online rapidamente."),
            },
            "websites": {
                "en": ("Website planning", "Pick the right layout and pages for your business."),
                "nl": ("Website planning", "Kies de juiste layout en paginas voor je bedrijf."),
                "fr": ("Planification site", "Choisissez la bonne mise en page pour votre activite."),
                "de": ("Website Planung", "Wahlen Sie Layout und Seiten fur Ihr Unternehmen."),
                "es": ("Plan web", "Elige el layout y paginas adecuados para tu negocio."),
                "pt": ("Plano do site", "Escolha layout e paginas certas para o seu negocio."),
            },
            "services": {
                "en": ("Service help", "Tell us what you need and we will map the next steps."),
                "nl": ("Service hulp", "Vertel wat je nodig hebt en we bepalen de stappen."),
                "fr": ("Aide services", "Dites-nous vos besoins et nous planifions la suite."),
                "de": ("Service Hilfe", "Sagen Sie uns, was Sie brauchen, wir planen weiter."),
                "es": ("Ayuda de servicios", "Dinos lo que necesitas y lo organizamos."),
                "pt": ("Ajuda de servicos", "Diga o que precisa e planeamos os passos."),
            },
            "pos-systems": {
                "en": ("POS setup", "Get help choosing the right POS tools."),
                "nl": ("POS setup", "Hulp bij het kiezen van de juiste POS tools."),
                "fr": ("Mise en place POS", "Aide pour choisir les bons outils POS."),
                "de": ("POS Einrichtung", "Hilfe bei der Wahl der richtigen POS Tools."),
                "es": ("Configuracion POS", "Ayuda para elegir las herramientas POS."),
                "pt": ("Configuracao POS", "Ajuda a escolher as ferramentas POS certas."),
            },
            "pos-systems-retail": {
                "en": ("Retail POS", "Shortlist POS systems for shops and boutiques."),
                "nl": ("Retail POS", "Shortlist POS systemen voor winkels en boutiques."),
                "fr": ("POS retail", "Shortlist POS pour boutiques et commerces."),
                "de": ("Retail POS", "Shortlist POS Systeme fuer Shops und Boutiquen."),
                "es": ("POS retail", "Shortlist POS para tiendas y boutiques."),
                "pt": ("POS retalho", "Shortlist POS para lojas e boutiques."),
            },
            "pos-systems-hospitality": {
                "en": ("Hospitality POS", "Find POS tools for cafes and restaurants."),
                "nl": ("POS horeca", "POS tools voor cafes en restaurants."),
                "fr": ("POS restauration", "POS pour cafes et restaurants."),
                "de": ("Gastro POS", "POS Tools fuer Cafes und Restaurants."),
                "es": ("POS hosteleria", "POS para cafes y restaurantes."),
                "pt": ("POS hotelaria", "POS para cafes e restaurantes."),
            },
            "pos-systems-compare": {
                "en": ("Compare POS", "Quick comparisons for pricing and features."),
                "nl": ("Vergelijk POS", "Snelle vergelijking van prijs en functies."),
                "fr": ("Comparer POS", "Comparaison rapide prix et fonctions."),
                "de": ("POS vergleichen", "Schneller Vergleich von Preis und Funktionen."),
                "es": ("Comparar POS", "Comparacion rapida de precio y funciones."),
                "pt": ("Comparar POS", "Comparacao rapida de preco e funcoes."),
            },
            "help-center": {
                "en": ("Need help?", "We can guide you to the right support option."),
                "nl": ("Hulp nodig?", "We helpen je naar de juiste support route."),
                "fr": ("Besoin d'aide?", "Nous vous orientons vers le bon support."),
                "de": ("Hilfe benotigt?", "Wir leiten Sie zum richtigen Support."),
                "es": ("Necesitas ayuda?", "Te guiamos al soporte correcto."),
                "pt": ("Precisa de ajuda?", "Orientamos para o suporte certo."),
            },
            "print-lab": {
                "en": ("Print support", "Get advice on formats, materials and delivery."),
                "nl": ("Print support", "Advies over formaten, materialen en levering."),
                "fr": ("Support impression", "Conseils sur formats, materiaux et livraison."),
                "de": ("Druck Support", "Tipps zu Formaten, Materialien und Lieferung."),
                "es": ("Soporte de impresion", "Consejos sobre formatos, materiales y entrega."),
                "pt": ("Suporte de impressao", "Conselhos sobre formatos e entregas."),
            },
            "print-lab-products": {
                "en": ("Print products", "Explore categories and white-label production."),
                "nl": ("Print producten", "Categorieen en white-label productie."),
                "fr": ("Produits print", "Categories et production white-label."),
                "de": ("Druckprodukte", "Kategorien und White-label Produktion."),
                "es": ("Productos print", "Categorias y produccion white-label."),
                "pt": ("Produtos print", "Categorias e producao white-label."),
            },
            "print-lab-how-it-works": {
                "en": ("How it works", "We sell, Printful fulfills and ships."),
                "nl": ("Hoe het werkt", "Wij verkopen, Printful produceert en verzendt."),
                "fr": ("Comment ca marche", "Nous vendons, Printful produit et expedie."),
                "de": ("So funktioniert es", "Wir verkaufen, Printful produziert und liefert."),
                "es": ("Como funciona", "Vendemos, Printful produce y envia."),
                "pt": ("Como funciona", "Vendemos, a Printful produz e envia."),
            },
            "print-lab-faq": {
                "en": ("Print Studio FAQ", "Returns and fulfillment details."),
                "nl": ("Print Studio FAQ", "Details over retouren en fulfillment."),
                "fr": ("Print Studio FAQ", "Details sur retours et fulfillment."),
                "de": ("Print Studio FAQ", "Details zu Retouren und Fulfillment."),
                "es": ("Print Studio FAQ", "Detalles de devoluciones y fulfillment."),
                "pt": ("Print Studio FAQ", "Detalhes de devolucoes e fulfillment."),
            },
            "products": {
                "en": ("Products overview", "Pick the tools you need for your site."),
                "nl": ("Producten overzicht", "Kies de tools die je nodig hebt."),
                "fr": ("Apercu produits", "Choisissez les bons outils."),
                "de": ("Produkte Uebersicht", "Waehlen Sie die passenden Tools."),
                "es": ("Resumen productos", "Elige los tools que necesitas."),
                "pt": ("Resumo produtos", "Escolha os tools de que precisa."),
            },
            "products-websites": {
                "en": ("Website builder", "Fast websites with clear messaging."),
                "nl": ("Website bouwer", "Snelle websites met duidelijke teksten."),
                "fr": ("Creation de site", "Sites rapides et clairs."),
                "de": ("Website Builder", "Schnelle Websites mit klarer Botschaft."),
                "es": ("Websites", "Websites rapidas y claras."),
                "pt": ("Websites", "Websites rapidas e claras."),
            },
            "products-seo": {
                "en": ("SEO tools", "Improve visibility and local search."),
                "nl": ("SEO tools", "Verbeter zichtbaarheid en lokaal zoeken."),
                "fr": ("Outils SEO", "Ameliorer la visibilite locale."),
                "de": ("SEO Tools", "Mehr Sichtbarkeit und Local Search."),
                "es": ("Tools SEO", "Mejora visibilidad y busqueda local."),
                "pt": ("Tools SEO", "Melhore visibilidade e pesquisa local."),
            },
            "products-print-studio": {
                "en": ("Print Studio", "White label printing via Printful."),
                "nl": ("Print Studio", "White label print via Printful."),
                "fr": ("Print Studio", "Impression white label via Printful."),
                "de": ("Print Studio", "White Label Druck via Printful."),
                "es": ("Print Studio", "Impresion white label via Printful."),
                "pt": ("Print Studio", "Impressao white label via Printful."),
            },
            "products-pos-systems": {
                "en": ("Card Payments", "Neutral POS guidance and partners."),
                "nl": ("POS-systemen", "Neutraal POS advies en partners."),
                "fr": ("Systemes POS", "Conseils POS et partenaires."),
                "de": ("POS-Systeme", "Neutrale POS Beratung."),
                "es": ("Sistemas POS", "Guia POS neutral y partners."),
                "pt": ("Sistemas POS", "Guia POS neutra e parceiros."),
            },
            "products-ads": {
                "en": ("Ads", "Local ads setup and reporting."),
                "nl": ("Ads", "Lokale ads en rapportage."),
                "fr": ("Ads", "Ads locales et reporting."),
                "de": ("Ads", "Lokale Ads und Reporting."),
                "es": ("Ads", "Ads locales y reporting."),
                "pt": ("Ads", "Ads locais e reporting."),
            },
            "products-uptime-status": {
                "en": ("Uptime Status", "Monitoring and uptime alerts."),
                "nl": ("Uptime status", "Monitoring en uptime alerts."),
                "fr": ("Uptime status", "Monitoring et alertes uptime."),
                "de": ("Uptime Status", "Monitoring und Uptime Alerts."),
                "es": ("Uptime status", "Monitoreo y alertas uptime."),
                "pt": ("Uptime status", "Monitorizacao e alertas uptime."),
            },
            "products-support": {
                "en": ("Support", "Fast answers and guidance."),
                "nl": ("Support", "Snelle antwoorden en begeleiding."),
                "fr": ("Support", "Reponses rapides et aide."),
                "de": ("Support", "Schnelle Antworten und Hilfe."),
                "es": ("Soporte", "Respuestas rapidas y ayuda."),
                "pt": ("Suporte", "Respostas rapidas e ajuda."),
            },
            "products-maintenance": {
                "en": ("Maintenance", "Keep your site updated."),
                "nl": ("Onderhoud", "Houd je site up to date."),
                "fr": ("Maintenance", "Gardez votre site a jour."),
                "de": ("Wartung", "Ihre Seite aktuell halten."),
                "es": ("Mantenimiento", "Mantener tu sitio al dia."),
                "pt": ("Manutencao", "Manter o site atualizado."),
            },
            "products-ecommerce": {
                "en": ("Ecommerce", "Simple store setup and orders."),
                "nl": ("Ecommerce", "Eenvoudige shop en orders."),
                "fr": ("Ecommerce", "Boutique simple et commandes."),
                "de": ("Ecommerce", "Einfacher Shop und Bestellungen."),
                "es": ("Ecommerce", "Tienda simple y pedidos."),
                "pt": ("Ecommerce", "Loja simples e encomendas."),
            },
            "billing": {
                "en": ("Billing help", "Questions about plans or invoices? We can help."),
                "nl": ("Billing hulp", "Vragen over plannen of facturen? Wij helpen."),
                "fr": ("Aide facturation", "Questions sur forfaits ou factures? On aide."),
                "de": ("Abrechnung Hilfe", "Fragen zu Planen oder Rechnungen? Wir helfen."),
                "es": ("Ayuda de facturacion", "Preguntas sobre planes o facturas? Te ayudamos."),
                "pt": ("Ajuda de faturacao", "Duvidas sobre planos ou faturas? Ajuda rapida."),
            },
            "billing-checkout": {
                "en": ("Checkout support", "Need help with checkout? Contact us."),
                "nl": ("Checkout hulp", "Hulp nodig bij checkout? Neem contact op."),
                "fr": ("Aide paiement", "Besoin d'aide au paiement? Contactez-nous."),
                "de": ("Checkout Hilfe", "Hilfe beim Checkout? Kontaktieren Sie uns."),
                "es": ("Ayuda en el pago", "Necesitas ayuda? Contactanos."),
                "pt": ("Ajuda no pagamento", "Precisa de ajuda? Fale connosco."),
            },
            "billing-success": {
                "en": ("Payment complete", "We can help you with next steps."),
                "nl": ("Betaling voltooid", "We helpen je met de volgende stappen."),
                "fr": ("Paiement termine", "Nous aidons pour la suite."),
                "de": ("Zahlung abgeschlossen", "Wir helfen bei den nachsten Schritten."),
                "es": ("Pago completado", "Te ayudamos con los siguientes pasos."),
                "pt": ("Pagamento concluido", "Ajudamos nos proximos passos."),
            },
            "billing-cancel": {
                "en": ("Payment cancelled", "Need assistance? We can help."),
                "nl": ("Betaling geannuleerd", "Hulp nodig? Wij helpen."),
                "fr": ("Paiement annule", "Besoin d'aide? Nous aidons."),
                "de": ("Zahlung abgebrochen", "Brauchen Sie Hilfe? Wir helfen."),
                "es": ("Pago cancelado", "Necesitas ayuda? Estamos aqui."),
                "pt": ("Pagamento cancelado", "Precisa de ajuda? Estamos aqui."),
            },
            "billing-portal": {
                "en": ("Billing portal", "Manage billing or reach support anytime."),
                "nl": ("Billing portal", "Beheer facturen of neem contact op."),
                "fr": ("Portail facturation", "Gerez la facturation ou contactez-nous."),
                "de": ("Abrechnungsportal", "Verwalten Sie oder kontaktieren Sie uns."),
                "es": ("Portal de facturacion", "Gestiona pagos o contacta soporte."),
                "pt": ("Portal de faturacao", "Gira faturas ou fale connosco."),
            },
            "printful": {
                "en": ("Printful help", "Need assistance with Printful setup?"),
                "nl": ("Printful hulp", "Hulp nodig bij Printful setup?"),
                "fr": ("Aide Printful", "Besoin d'aide avec Printful?"),
                "de": ("Printful Hilfe", "Hilfe bei Printful Einrichtung?"),
                "es": ("Ayuda Printful", "Ayuda con la configuracion Printful?"),
                "pt": ("Ajuda Printful", "Ajuda na configuracao Printful?"),
            },
            "printful-products": {
                "en": ("Product setup", "We can help with product listings."),
                "nl": ("Product setup", "Hulp met product listings."),
                "fr": ("Config produits", "Aide pour les listes produits."),
                "de": ("Produkt Setup", "Hilfe bei Produktlisten."),
                "es": ("Config productos", "Ayuda con listas de productos."),
                "pt": ("Config produtos", "Ajuda com listas de produtos."),
            },
            "printful-orders": {
                "en": ("Order support", "Questions about orders? We can help."),
                "nl": ("Order support", "Vragen over orders? Wij helpen."),
                "fr": ("Support commandes", "Questions sur les commandes? On aide."),
                "de": ("Bestell Support", "Fragen zu Bestellungen? Wir helfen."),
                "es": ("Soporte pedidos", "Preguntas sobre pedidos? Ayudamos."),
                "pt": ("Suporte encomendas", "Duvidas sobre encomendas? Ajuda rapida."),
            },
        }

        for slug in page_translations.keys():
            page_obj = Page.objects.filter(slug=slug).first()
            if not page_obj:
                continue
            panel, _ = RightSidebarPanel.objects.get_or_create(
                page=page_obj,
                defaults={
                    "is_enabled": True,
                    "phone": default_panel.phone,
                    "email": default_panel.email,
                    "address": default_panel.address,
                    "maps_url": default_panel.maps_url,
                    "cta_url": default_panel.cta_url,
                    "show_social": default_panel.show_social,
                },
            )
            for lang in languages:
                headline, intro = page_sidebar_copy.get(slug, {}).get(
                    lang,
                    page_sidebar_copy["home"][lang],
                )
                panel.set_current_language(lang)
                panel.headline = headline
                panel.intro = intro
                panel.cta_text = default_translations[lang]["cta_text"]
                panel.extra_html = default_translations[lang]["extra_html"]
                panel.save()

        self.stdout.write(self.style.SUCCESS("Seeded JCW pages and sections."))
