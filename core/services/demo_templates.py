from types import SimpleNamespace

from django.utils.text import slugify
from django.utils.translation import gettext_lazy as _


def _build_demo(slug, style_key, **data):
    return {
        "slug": slug,
        "style_key": style_key,
        "url_slug": slugify(slug),
        **data,
    }


DEMO_TEMPLATES = {
    "beauty-spa": _build_demo(
        "beauty-spa",
        "beauty",
        category=_("Beauty / Spa"),
        title=_("Luna Beauty Studio"),
        tagline=_("Beauty / Spa demo template"),
        description=_(
            "A calm, elegant demo website for salons, beauty rooms, and wellness services."
        ),
        summary=_(
            "Designed for appointment-based businesses that want a polished online presence."
        ),
        preview_brand=_("Luna"),
        preview_nav=[_("Treatments"), _("Prices"), _("About"), _("Book")],
        preview_nav_cta=_("Book now"),
        preview_contact_email=_("hello@lunabeauty-demo.com"),
        preview_contact_phone=_("+31 20 480 2211"),
        preview_contact_note=_("Appointments Tuesday to Saturday"),
        preview_footer_links=[_("Treatments"), _("Gift cards"), _("Visit us")],
        preview_footer_note=_("Quiet, elegant care in the centre of the city."),
        preview_trust=[
            _("Private treatment room"),
            _("Evening appointments"),
            _("Gift vouchers available"),
        ],
        preview_quote_title=_("A calmer beauty experience"),
        preview_quote_text=_(
            "Designed for clients who want clear treatment information, a polished first impression, and an easy path to booking."
        ),
        preview_quote_caption=_("Soft editorial homepage direction"),
        preview_reviews=[
            {
                "name": _("New client visits"),
                "text": _("A gentle first-time booking journey with trust-building treatment highlights."),
            },
            {
                "name": _("Repeat appointments"),
                "text": _("Room for maintenance services, package offers, and seasonal care updates."),
            },
        ],
        hero_title=_("A polished beauty website that feels calm, clear, and ready to book"),
        hero_text=_(
            "This locked demo shows how a beauty or spa business can present treatments, build trust, and guide visitors toward bookings."
        ),
        primary_cta=_("Request this style"),
        secondary_cta=_("View pricing"),
        stats=[
            _("Soft editorial look"),
            _("Service-led homepage"),
            _("Built for local bookings"),
        ],
        services=[
            {
                "name": _("Signature facials"),
                "text": _("Treatment overview with clear pricing and a clean benefits summary."),
            },
            {
                "name": _("Brows & lashes"),
                "text": _("Focused service highlights for repeat clients and first-time visitors."),
            },
            {
                "name": _("Body treatments"),
                "text": _("A premium section layout for add-ons, packages, and seasonal offers."),
            },
        ],
        highlights=[
            _("Elegant hero and trust-focused introduction"),
            _("Clear treatment sections with service hierarchy"),
            _("Space for testimonials, opening hours, and contact details"),
        ],
        sections=[
            {
                "title": _("Calm visual direction"),
                "text": _(
                    "Soft colors, refined spacing, and service-first copy help the business feel premium without being complicated."
                ),
            },
            {
                "title": _("Built for local discovery"),
                "text": _(
                    "This structure supports local clients who want to check treatments, pricing cues, and booking information quickly."
                ),
            },
            {
                "title": _("Ready to clone later"),
                "text": _(
                    "The demo is intentionally curated as a locked master so it can later be copied into a customer site without mutating the original."
                ),
            },
        ],
        faq=[
            {
                "question": _("Who is this demo for?"),
                "answer": _(
                    "Beauty rooms, nail studios, brow bars, massage practices, and other appointment-led service businesses."
                ),
            },
            {
                "question": _("Can this style be adapted later?"),
                "answer": _(
                    "Yes. The master demo stays locked, while a future cloned version can be adjusted for a real business."
                ),
            },
        ],
        showcase_description=_(
            "Soft, elegant styling for treatments, trust-building, and local bookings."
        ),
    ),
    "construction-services": _build_demo(
        "construction-services",
        "construction",
        category=_("Construction / Services"),
        title=_("Northline Property Services"),
        tagline=_("Construction / Services demo template"),
        description=_(
            "A strong, practical demo website for trades, installation businesses, and local service teams."
        ),
        summary=_(
            "Designed for businesses that need clarity, credibility, and clear service visibility."
        ),
        preview_brand=_("Northline"),
        preview_nav=[_("Services"), _("Projects"), _("Coverage"), _("Request quote")],
        preview_nav_cta=_("Call today"),
        preview_contact_email=_("office@northline-demo.com"),
        preview_contact_phone=_("+31 10 440 1288"),
        preview_contact_note=_("Mon to Fri, 08:00 to 17:30"),
        preview_footer_links=[_("Renovation"), _("Maintenance"), _("Commercial work")],
        preview_footer_note=_("Reliable property work with clear communication and practical scheduling."),
        preview_trust=[
            _("Fully insured"),
            _("Clear quotations"),
            _("Local project coverage"),
        ],
        preview_quote_title=_("Built for service businesses that need trust fast"),
        preview_quote_text=_(
            "This direction puts service categories, project proof, and contact routes in front of the visitor quickly."
        ),
        preview_quote_caption=_("Practical, quote-led service homepage"),
        preview_reviews=[
            {
                "name": _("Project visibility"),
                "text": _("Space for recent jobs, before-and-after proof, and service-area clarity."),
            },
            {
                "name": _("Fast enquiries"),
                "text": _("Clear quote prompts and phone-first contact paths for urgent or practical work."),
            },
        ],
        hero_title=_("A professional service website built to show work clearly and earn trust fast"),
        hero_text=_(
            "This locked demo shows how a construction or field-service business can present its work, explain services, and make enquiries easier."
        ),
        primary_cta=_("Request this style"),
        secondary_cta=_("View pricing"),
        stats=[
            _("Strong service structure"),
            _("Built for trust"),
            _("Clear local positioning"),
        ],
        services=[
            {
                "name": _("Renovation services"),
                "text": _("A clear layout for projects, capabilities, and service areas."),
            },
            {
                "name": _("Repairs & maintenance"),
                "text": _("Service blocks designed for fast scanning and straightforward enquiries."),
            },
            {
                "name": _("Commercial work"),
                "text": _("Space for larger project types, compliance notes, and credibility points."),
            },
        ],
        highlights=[
            _("Bold hero with trust markers and structured sections"),
            _("Practical cards for service categories and project examples"),
            _("Clear enquiry flow for local service businesses"),
        ],
        sections=[
            {
                "title": _("Service-first layout"),
                "text": _(
                    "The structure is built to explain what the business does, where it operates, and why customers should trust it."
                ),
            },
            {
                "title": _("Credibility before complexity"),
                "text": _(
                    "Project highlights, review areas, and process blocks help the site feel dependable without becoming overloaded."
                ),
            },
            {
                "title": _("Controlled master template"),
                "text": _(
                    "This demo remains a curated reference example until a separate clone flow is introduced for customer sites."
                ),
            },
        ],
        faq=[
            {
                "question": _("What kind of businesses does this fit?"),
                "answer": _(
                    "Builders, installers, maintenance teams, property services, and other local trade-based businesses."
                ),
            },
            {
                "question": _("Is this connected to a real customer site?"),
                "answer": _(
                    "No. It is a locked demonstration template created only for public preview and future cloning."
                ),
            },
        ],
        showcase_description=_(
            "Strong, clean styling for trades, property services, and local credibility."
        ),
    ),
    "restaurant-food": _build_demo(
        "restaurant-food",
        "restaurant",
        category=_("Restaurant / Food"),
        title=_("Table & Flame Kitchen"),
        tagline=_("Restaurant / Food demo template"),
        description=_(
            "A warm, inviting demo website for restaurants, cafes, takeaways, and food brands."
        ),
        summary=_(
            "Designed for food businesses that need atmosphere, clear menus, and practical visitor information."
        ),
        preview_brand=_("Table & Flame"),
        preview_nav=[_("Menu"), _("Reservations"), _("Story"), _("Visit")],
        preview_contact_email=_("hello@tableandflame-demo.com"),
        preview_contact_phone=_("+31 30 555 0144"),
        preview_contact_note=_("Open Wednesday to Sunday"),
        preview_footer_links=[_("Menu"), _("Private dining"), _("Location")],
        hero_title=_("A food website that feels inviting, easy to browse, and ready for real customers"),
        hero_text=_(
            "This locked demo shows how a restaurant or food business can present menus, opening hours, and key details in a way that feels welcoming."
        ),
        primary_cta=_("Request this style"),
        secondary_cta=_("View pricing"),
        stats=[
            _("Warm visual identity"),
            _("Menu-friendly structure"),
            _("Built for local discovery"),
        ],
        services=[
            {
                "name": _("Menu highlights"),
                "text": _("Sections for featured dishes, specials, and seasonal promotions."),
            },
            {
                "name": _("Visit information"),
                "text": _("Opening hours, contact details, and practical location content."),
            },
            {
                "name": _("Brand atmosphere"),
                "text": _("A warmer presentation layer that supports photos, offers, and trust-building."),
            },
        ],
        highlights=[
            _("Warm hero treatment with food-first content flow"),
            _("Space for menus, opening hours, and featured dishes"),
            _("Built to guide visitors toward visiting, booking, or ordering"),
        ],
        sections=[
            {
                "title": _("Designed for hospitality"),
                "text": _(
                    "The layout gives food businesses room to create atmosphere while still keeping the most practical information easy to find."
                ),
            },
            {
                "title": _("Simple content structure"),
                "text": _(
                    "Menu categories, specials, location details, and contact prompts are organized for quick scanning on mobile and desktop."
                ),
            },
            {
                "title": _("Locked master demo"),
                "text": _(
                    "This preview stays separate from live customer websites so it can serve as a stable base for future copy-and-customize flows."
                ),
            },
        ],
        faq=[
            {
                "question": _("Is this meant for restaurants only?"),
                "answer": _(
                    "No. It also fits cafes, takeaways, bakeries, and other food-led local businesses."
                ),
            },
            {
                "question": _("Can the demo be reused later?"),
                "answer": _(
                    "Yes. The structure is intentionally organized so a future clone flow can turn it into a separate customer website."
                ),
            },
        ],
        showcase_description=_(
            "Warm, inviting styling for menus, opening hours, and hospitality-focused visibility."
        ),
    ),
}


STYLE_PRESETS = {
    "beauty": {
        "hero_bg": "from-rose-100 via-stone-50 to-pink-100",
        "hero_ring": "ring-rose-200/70",
        "badge": "bg-white/80 text-rose-700",
        "accent_text": "text-rose-700",
        "accent_bg": "bg-rose-600 hover:bg-rose-700",
        "surface": "bg-white/80",
        "preview_bg": "from-rose-200 via-pink-100 to-stone-100",
        "preview_accent": "bg-rose-500/80",
    },
    "construction": {
        "hero_bg": "from-slate-200 via-white to-amber-100",
        "hero_ring": "ring-slate-300/80",
        "badge": "bg-white/85 text-amber-700",
        "accent_text": "text-amber-700",
        "accent_bg": "bg-slate-900 hover:bg-slate-800",
        "surface": "bg-white/85",
        "preview_bg": "from-slate-700 via-slate-800 to-amber-500",
        "preview_accent": "bg-amber-400/90",
    },
    "restaurant": {
        "hero_bg": "from-orange-100 via-amber-50 to-red-100",
        "hero_ring": "ring-orange-200/80",
        "badge": "bg-white/85 text-orange-700",
        "accent_text": "text-orange-700",
        "accent_bg": "bg-orange-600 hover:bg-orange-700",
        "surface": "bg-white/85",
        "preview_bg": "from-orange-300 via-amber-200 to-red-200",
        "preview_accent": "bg-red-500/85",
    },
}


def _namespace(value):
    if isinstance(value, dict):
        return SimpleNamespace(**{key: _namespace(item) for key, item in value.items()})
    if isinstance(value, list):
        return [_namespace(item) for item in value]
    return value


def get_demo_template(slug):
    demo = DEMO_TEMPLATES.get(slug)
    if not demo:
        return None
    return _namespace({**demo, "styles": STYLE_PRESETS[demo["style_key"]]})


def get_demo_showcase_cards():
    cards = []
    for demo in DEMO_TEMPLATES.values():
        cards.append(
            _namespace(
                {
                    "slug": demo["slug"],
                    "title": demo["title"],
                    "category": demo["category"],
                    "description": demo["showcase_description"],
                    "styles": STYLE_PRESETS[demo["style_key"]],
                }
            )
        )
    return cards
