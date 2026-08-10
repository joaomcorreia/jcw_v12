from django.contrib.auth import get_user_model
from django.test import TestCase, override_settings

from core.models import Plan, Site


User = get_user_model()


@override_settings(
    SEO_NOINDEX=False,
    GA_MEASUREMENT_ID="G-41FT24DKC0",
    CLARITY_PROJECT_ID="xzzv2ck6mf",
    BING_SITE_VERIFICATION="2265E66186640799AB827F84D8FAC5F1",
)
class PublicAnalyticsConsentTests(TestCase):
    @classmethod
    def setUpTestData(cls):
        owner = User.objects.create_user(username="analytics-owner", password="testpass123")
        plan = Plan.objects.create(key="analytics-plan", slug="analytics-plan")
        Site.objects.create(
            owner=owner,
            plan=plan,
            name="Just Code Works",
            subdomain="justcodeworks",
            language="en",
            status=Site.STATUS_PUBLISHED,
            is_main=True,
        )

    def test_public_languages_render_configured_verification_and_consent_ui(self):
        for language in ("en", "de", "es", "fr", "nl", "pt"):
            response = self.client.get(f"/{language}/", HTTP_HOST="justcodeworks.local")
            self.assertEqual(response.status_code, 200)
            body = response.content.decode()
            self.assertIn('name="msvalidate.01"', body)
            self.assertIn("G\\u002D41FT24DKC0", body)
            self.assertIn("xzzv2ck6mf", body)
            self.assertIn("data-analytics-consent-action=\"accept\"", body)
            self.assertIn("data-analytics-consent-action=\"reject\"", body)
            self.assertNotIn("w0rrp5mkxz", body)
            self.assertEqual(body.count("G\\u002D41FT24DKC0"), 1)
            self.assertEqual(body.count("xzzv2ck6mf"), 1)
            self.assertEqual(body.count('name="msvalidate.01"'), 1)

    def test_privacy_page_is_available_in_all_languages_with_seo_and_links(self):
        for language in ("en", "de", "es", "fr", "nl", "pt"):
            response = self.client.get(
                f"/{language}/privacy-cookies/",
                HTTP_HOST="justcodeworks.local",
            )
            self.assertEqual(response.status_code, 200)
            body = response.content.decode()
            self.assertIn(f'hreflang="{language}"', body)
            self.assertIn(f'canonical" href="http://justcodeworks.local/{language}/privacy-cookies/"', body)
            self.assertIn(f'href="/{language}/privacy-cookies/"', body)
            self.assertIn("Privacy", body)
            self.assertEqual(body.count("xzzv2ck6mf"), 1)
            self.assertNotIn("w0rrp5mkxz", body)

    def test_public_footer_and_consent_notice_link_to_privacy_page(self):
        response = self.client.get("/nl/", HTTP_HOST="justcodeworks.local")
        body = response.content.decode()
        self.assertIn('href="/nl/privacy-cookies/"', body)
        self.assertIn("Learn more", body)
        response = self.client.get("/nl/privacy-cookies/", HTTP_HOST="justcodeworks.local")
        self.assertIn('href="/nl/privacy-cookies/"', response.content.decode())
    def test_internal_pages_do_not_receive_public_analytics_markup(self):
        for path in ("/en/control-panel/", "/admin/"):
            response = self.client.get(path, HTTP_HOST="justcodeworks.local")
            self.assertNotIn("G-41FT24DKC0", response.content.decode())
            self.assertNotIn("xzzv2ck6mf", response.content.decode())

    def test_consent_controller_fails_closed_until_choice(self):
        with open("static/jcw/js/analytics-consent.js", encoding="utf-8") as source:
            script = source.read()
        self.assertIn('analytics_storage: "denied"', script)
        self.assertIn('ad_storage: "denied"', script)
        self.assertIn('var storageKey = "jcw-analytics-consent";', script)
        self.assertIn('localStorage.setItem(storageKey, value)', script)
        self.assertIn('window.clarity("consent", true)', script)
        self.assertIn("googletagmanager.com/gtag/js", script)
        self.assertIn("clarity.ms/tag/", script)