"""
Main Site URL Configuration (core app)

This URLConf is included by config/urls.py for the MAIN site only (justcodeworks.local).
Tenant sites use config/tenants/urls.py which includes core/urls_tenant.py instead.

ROUTING INVARIANTS:
- Dashboard routes are NOT included here - they live in core/urls_dashboard.py
- Dashboard (/dashboard/) is only available on tenant subdomains
- Control panel (/control-panel/) is only available on main site (config/urls.py)
- Main site never exposes /dashboard/ - users access their tenant dashboard via subdomain
"""
from django.urls import path
from django.views.generic import RedirectView

from . import views

app_name = "core"

urlpatterns = [
    # Main site public pages
    path("", views.home, name="home"),
    path("about/", views.about, name="about"),
    path("what-we-build/", views.what_we_build, name="what_we_build"),
    path("how-we-work/", views.how_we_work, name="how_we_work"),
    # Main site API endpoints (used by marketing editor)
    path("main/api/main-section-settings/", views.main_section_settings, name="main_section_settings"),
    path("main/api/main-inline-save/", views.main_inline_save, name="main_inline_save"),
    # Legacy endpoint - deprecated, will be removed
    path("dashboard/api/section-settings/", views.main_section_settings, name="main_section_settings_legacy"),
    path("signup/", views.signup_view, name="signup"),
    path("start/", views.start_design, name="start_design"),
    path("onboarding/step-1/", views.onboarding_step1, name="onboarding_step1"),
    path("onboarding/step-2/", views.onboarding_step2, name="onboarding_step2"),
    path("onboarding/step-3/", views.onboarding_step3, name="onboarding_step3"),
    path("onboarding/complete/", views.complete_draft, name="complete_draft"),
    path("onboarding/", views.onboarding, name="onboarding"),
    path("dashboard/website/preview/", views.website_preview, name="website_preview"),
    path("accounts/signup/", views.signup, name="signup"),
    # Products & services
    path("websites/", views.websites, name="websites"),
    path("products/", views.products_index, name="products_index"),
    path("products/websites/", views.product_websites, name="product_websites"),
    path("products/seo/", views.product_seo, name="product_seo"),
    path("products/print-studio/", views.product_print_studio, name="product_print_studio"),
    path("products/pos-systems/", views.product_pos_systems, name="product_pos_systems"),
    path("products/ads/", views.product_ads, name="product_ads"),
    path("products/uptime-status/", views.product_uptime_status, name="product_uptime_status"),
    path("products/support/", views.product_support, name="product_support"),
    path("products/maintenance/", views.product_maintenance, name="product_maintenance"),
    path("products/ecommerce/", views.product_ecommerce, name="product_ecommerce"),
    path("websites/one-page/", views.websites_one_page, name="websites_one_page"),
    path("websites/how-it-works/", views.websites, name="websites_how_it_works"),
    path("websites/jcw-system/", views.websites_jcw_system, name="websites_jcw_system"),
    path("websites/wordpress/", views.websites_wordpress, name="websites_wordpress"),
    path("websites/multi-page/", RedirectView.as_view(pattern_name="core:websites_how_it_works", permanent=True), name="websites_multi_page"),
    path("websites/multi-page-seo/", views.websites_multi_page_seo, name="websites_multi_page_seo"),
    path("websites/catalog-site/", views.websites_catalog_site, name="websites_catalog_site"),
    path("websites/ecommerce/", RedirectView.as_view(pattern_name="core:websites_how_it_works", permanent=True), name="websites_ecommerce"),
    path("websites/eshop-starter/", views.websites_eshop_starter, name="websites_eshop_starter"),
    path("websites/starter-estore/", views.websites_eshop_starter, name="websites_starter_estore"),
    path("websites/eshop-premium/", views.websites_eshop_premium, name="websites_eshop_premium"),
    path("websites/custom/", views.websites_custom, name="websites_custom"),
    path("websites/custom-website/", views.websites_custom, name="websites_custom_website"),
    path("pricing/", views.pricing, name="pricing"),
    path("contact/", views.contact, name="contact"),
    path("demos/<slug:slug>/", views.demo_preview, name="demo_preview"),
    path("online-marketing/", views.online_marketing, name="online_marketing"),
    path("facebook-visibility/", views.facebook_visibility, name="facebook_visibility"),
    path("services/", views.services, name="services"),
    # POS systems
    path("pos-systems/", views.pos_systems, name="pos_systems"),
    path("pos-systems/retail/", views.pos_systems_retail, name="pos_systems_retail"),
    path("pos-systems/hospitality/", views.pos_systems_hospitality, name="pos_systems_hospitality"),
    path("pos-systems/services/", views.pos_systems_services, name="pos_systems_services"),
    path("pos-systems/compare/", views.pos_systems_compare, name="pos_systems_compare"),
    path("pos-systems/faq/", views.pos_systems_faq, name="pos_systems_faq"),
    # Help & blog
    path("help/", views.help_page, name="help"),
    path("help-center/", views.help_center, name="help_center"),
    path("blog/", views.blog_index, name="blog_index"),
    path("blog/<slug:slug>/", views.blog_detail, name="blog_detail"),
    # Print lab (with legacy redirects)
    path("print-lab/", RedirectView.as_view(pattern_name="core:printlab", permanent=False), name="print_lab"),
    path("print-lab/products/", RedirectView.as_view(pattern_name="core:printlab", permanent=False)),
    path("print-lab/how-it-works/", RedirectView.as_view(pattern_name="core:printlab", permanent=False)),
    path("print-lab/faq/", RedirectView.as_view(pattern_name="core:printlab", permanent=False)),
    path("print/", views.print_overview, name="print_overview"),
    path("print/business/", views.print_business, name="print_business"),
    path("print/merch/", views.print_merch, name="print_merch"),
    path("printlab/", views.printlab, name="printlab"),
    path("printlab/start/", views.printlab_start, name="printlab_start"),
    path("printlab/business-cards/", views.printlab_business_cards, name="printlab_business_cards"),
    path("printlab/flyers/", views.printlab_flyers, name="printlab_flyers"),
    path("printlab/brochures/", views.printlab_brochures, name="printlab_brochures"),
    path("printlab/stickers/", views.printlab_stickers, name="printlab_stickers"),
    path("printlab/apparel/", views.printlab_apparel, name="printlab_apparel"),
    path("printlab/merch/", views.printlab_merch, name="printlab_merch"),
    # Billing (main site user billing, not tenant dashboard billing)
    path("billing/", views.billing, name="billing"),
    path("billing/checkout/", views.billing_checkout, name="billing_checkout"),
    path("billing/success/", views.billing_success, name="billing_success"),
    path("billing/cancel/", views.billing_cancel, name="billing_cancel"),
    path("billing/portal/", views.billing_portal, name="billing_portal"),
    # Printful integration
    path("printful/", views.printful, name="printful"),
    path("printful/products/", views.printful_products, name="printful_products"),
    path("printful/orders/", views.printful_orders, name="printful_orders"),
    # Location pages
    path("locations/<str:country>/", views.location_country, name="public_location_country"),
    path("locations/<str:country>/<slug:city>/", views.location_city, name="public_location"),
    # Catch-all for dynamic pages (must be last)
    path("<slug:slug>/", views.public_page, name="public_page"),
]
