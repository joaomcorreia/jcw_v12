from unittest.mock import Mock, patch

from django.contrib.auth import get_user_model
from django.test import TestCase, override_settings

from core.models import AssistantProfile, Plan, Site
from core.services.assistant_profile import ensure_assistant_profile


User = get_user_model()


@override_settings(SEO_NOINDEX=False)
class PublicReleaseTests(TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.owner = User.objects.create_user(username="release-owner", password="testpass123")
        cls.plan = Plan.objects.create(key="release-plan", slug="release-plan")
        cls.main_site = Site.objects.create(
            owner=cls.owner,
            plan=cls.plan,
            name="Just Code Works",
            subdomain="justcodeworks",
            language="en",
            status=Site.STATUS_PUBLISHED,
            is_main=True,
        )

    def test_only_approved_public_pages_are_indexable_in_all_languages(self):
        for language in ("en", "de", "es", "fr", "nl", "pt"):
            for path in ("", "about/", "what-we-build/", "how-we-work/", "contact/"):
                response = self.client.get(f"/{language}/{path}", HTTP_HOST="justcodeworks.local")
                self.assertEqual(response.status_code, 200, f"/{language}/{path}")
                self.assertNotIn("noindex", response.get("X-Robots-Tag", "").lower())
                self.assertIn(b'content="index, follow"', response.content)
                self.assertIn(b'rel="canonical"', response.content)
                self.assertIn(b'hreflang="x-default"', response.content)

    def test_internal_route_remains_non_indexable_and_protected(self):
        response = self.client.get("/en/control-panel/", HTTP_HOST="justcodeworks.local")
        self.assertIn(response.status_code, {302, 403})
        self.assertIn("noindex", response.get("X-Robots-Tag", "").lower())
        response = self.client.get("/admin/", HTTP_HOST="justcodeworks.local")
        self.assertIn(response.status_code, {302, 403})
        self.assertIn("noindex", response.get("X-Robots-Tag", "").lower())

    def test_robots_and_sitemap_contain_only_public_allowlist(self):
        robots = self.client.get("/robots.txt", HTTP_HOST="justcodeworks.local")
        body = robots.content.decode()
        self.assertEqual(robots.status_code, 200)
        self.assertIn("Disallow: /", body)
        self.assertIn("Allow: /en/$", body)
        self.assertIn("Allow: /pt/contact/$", body)
        self.assertNotIn("Allow: /en/control-panel", body)
        sitemap = self.client.get("/sitemap.xml", HTTP_HOST="justcodeworks.local")
        sitemap_body = sitemap.content.decode()
        for language in ("en", "de", "es", "fr", "nl", "pt"):
            self.assertIn(f"/sitemap-{language}.xml", sitemap_body)
        self.assertNotIn("control-panel", sitemap_body)
        language_sitemap = self.client.get("/sitemap-pt.xml", HTTP_HOST="justcodeworks.local")
        self.assertIn("/pt/contact/", language_sitemap.content.decode())
        self.assertNotIn("/en/contact/", language_sitemap.content.decode())

    def test_public_assistant_is_frontend_only_and_main_site_scoped(self):
        profile = ensure_assistant_profile(self.main_site)
        profile.frontend_enabled = True
        profile.save(update_fields=["frontend_enabled", "updated_at"])
        fake_response = Mock(output_text="Resposta segura em portugues europeu.")
        fake_client = Mock()
        fake_client.responses.create.return_value = fake_response
        with patch("core.views.request_assistant_response", return_value=(fake_response.output_text, {"languages": {"conversation_language": "pt"}})) as request:
            response = self.client.post(
                "/pt/api/assistant/chat/",
                {"message": "O que faz a JCW?", "conversation_language": "pt"},
                HTTP_HOST="justcodeworks.local",
            )
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json()["answer"], fake_response.output_text)
        request.assert_called_once()
        self.assertEqual(request.call_args.kwargs["surface"], "frontend")
        self.assertEqual(request.call_args.kwargs["content_language"], "pt")
        homepage = self.client.get("/pt/", HTTP_HOST="justcodeworks.local")
        self.assertIn(b"data-jcw-assistant-endpoint", homepage.content)
        self.assertNotIn(b"control-panel", response.content)