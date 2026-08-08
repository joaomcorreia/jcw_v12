from django.conf import settings
from django.contrib.auth import get_user_model
from django.test import TestCase, Client
from django.urls import reverse

from core.models import Plan, Site


User = get_user_model()


class LanguageRoutingTests(TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.staff = User.objects.create_user(
            username="language-staff",
            password="testpass123",
            is_staff=True,
        )
        cls.tenant_owner = User.objects.create_user(
            username="language-tenant",
            password="testpass123",
        )
        cls.plan = Plan.objects.create(key="language-test-plan", slug="language-test-plan")
        cls.tenant = Site.objects.create(
            name="Language Test Tenant",
            subdomain="language-test",
            owner=cls.tenant_owner,
            plan=cls.plan,
            language="en",
        )

    def test_root_maps_browser_languages_and_unsupported_to_english(self):
        cases = (
            ("de-DE,de;q=0.8", "/de/"),
            ("pt-BR,pt;q=0.9", "/pt/"),
            ("ja-JP,ja;q=0.9", "/en/"),
        )
        for header, expected in cases:
            response = self.client.get(
                "/",
                HTTP_HOST="justcodeworks.local",
                HTTP_ACCEPT_LANGUAGE=header,
            )
            self.assertRedirects(response, expected, fetch_redirect_response=False)

    def test_explicit_cookie_overrides_browser_language(self):
        self.client.cookies[settings.LANGUAGE_COOKIE_NAME] = "fr"
        response = self.client.get(
            "/",
            HTTP_HOST="justcodeworks.local",
            HTTP_ACCEPT_LANGUAGE="de-DE",
        )
        self.assertRedirects(response, "/fr/", fetch_redirect_response=False)

    def test_manual_language_selection_persists_and_preserves_page(self):
        response = self.client.post(
            "/en/i18n/setlang/",
            {"language": "de", "next": "/en/about/?source=test"},
            HTTP_HOST="justcodeworks.local",
        )
        self.assertRedirects(
            response,
            "/de/about/?source=test",
            fetch_redirect_response=False,
        )
        self.assertEqual(
            self.client.cookies[settings.LANGUAGE_COOKIE_NAME].value,
            "de",
        )

        response = self.client.get(
            "/",
            HTTP_HOST="justcodeworks.local",
            HTTP_ACCEPT_LANGUAGE="fr-FR",
        )
        self.assertRedirects(response, "/de/", fetch_redirect_response=False)

    def test_home_navigation_and_cta_use_active_language(self):
        for code in ("en", "de", "es", "fr", "nl", "pt"):
            response = self.client.get(f"/{code}/", HTTP_HOST="justcodeworks.local")
            body = response.content.decode("utf-8")
            self.assertIn(f"/{code}/what-we-build/", body)
            self.assertIn(f"/{code}/contact/", body)
            self.assertIn("data-jcw-clippy-open", body)
            if code != "en":
                self.assertNotIn("/en/contact/", body)

    def test_prefixed_urls_do_not_redirect_to_another_language(self):
        for code in ("en", "de", "es", "fr", "nl", "pt"):
            response = self.client.get(f"/{code}/", HTTP_HOST="justcodeworks.local")
            self.assertEqual(response.status_code, 200)

    def test_tenant_language_prefix_preserves_host_context(self):
        self.client.login(username="language-tenant", password="testpass123")
        for code in ("en", "de", "es", "fr", "nl", "pt"):
            response = self.client.get(
                f"/{code}/dashboard/",
                HTTP_HOST="language-test.justcodeworks.local",
            )
            self.assertEqual(response.status_code, 200)
            self.assertEqual(response.wsgi_request.tenant, self.tenant)

    def test_staff_control_panel_resolves_in_all_languages(self):
        self.client.login(username="language-staff", password="testpass123")
        for code in ("en", "de", "es", "fr", "nl", "pt"):
            response = self.client.get(
                f"/{code}/control-panel/",
                HTTP_HOST="justcodeworks.local",
            )
            self.assertEqual(response.status_code, 200)
