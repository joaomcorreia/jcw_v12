"""
Regression tests for main site vs tenant site isolation.

MANUAL TESTING CHECKLIST:
=========================

1. TENANT SITE (e.g., mim.justcodeworks.local)
   - [ ] Load tenant home page
   - [ ] Verify window.JCW_SITE_MODE === "tenant" in console
   - [ ] Verify NO [data-jcw-hero-slider] element exists in DOM
   - [ ] Verify NO #jcw-hero-settings JSON script tag exists
   - [ ] Verify NO editor.js is loaded (check Network tab)
   - [ ] Verify NO editor.css is loaded
   - [ ] Verify NO #jcw-editor-bar exists
   - [ ] Console should NOT show "JCW editor loaded"
   - [ ] Body should NOT have jcw-edit-mode class even with ?edit=1

2. MAIN SITE (justcodeworks.local)
   - [ ] Load main home page
   - [ ] Verify window.JCW_SITE_MODE === "main" in console
   - [ ] Verify [data-jcw-hero-slider="1"] exists on hero section
   - [ ] Verify #jcw-hero-settings JSON script exists
   - [ ] Verify editor.js loads (when ?edit=1 and logged in as staff)
   - [ ] Verify body has jcw-edit-mode class when ?edit=1
   - [ ] Verify #jcw-editor-bar exists with Hero Settings button
   - [ ] Console should show "JCW editor loaded"
   - [ ] Click "Hero Settings" button - modal should open
   - [ ] Change a hero setting and save
   - [ ] Verify save calls /<lang>/main/api/main-section-settings/
   - [ ] Verify settings persist in MainSiteSectionSettings (not TenantHeroSettings)

3. API ENDPOINT PROTECTION
   - [ ] POST to /<lang>/main/api/main-section-settings/ from tenant host should 403
   - [ ] POST to /<lang>/dashboard/api/section-settings/ from main host should 403
   - [ ] Non-staff user should get 403 on main section settings

4. DATABASE ISOLATION
   - [ ] After saving hero settings on main site, verify MainSiteSectionSettings updated
   - [ ] Verify TenantHeroSettings for any tenant is NOT modified
   - [ ] Tenant dashboard changes should only update TenantHeroSettings

5. CLASS CONSISTENCY
   - [ ] editor.js uses jcw-edit-mode consistently (not edit-mode)
   - [ ] Templates add jcw-edit-mode class when is_edit_mode is True
   - [ ] Event handlers check for jcw-edit-mode class
"""

from django.test import TestCase, Client, RequestFactory, override_settings
from django.urls import reverse
from django.contrib.auth import get_user_model
from core.models import Site, Plan, MainSiteSectionSettings, TenantHeroSettings
from core import views as core_views
import json

User = get_user_model()


class MainSiteIsolationTest(TestCase):
    """Tests for main site hero settings isolation."""

    @classmethod
    def setUpTestData(cls):
        cls.staff_user = User.objects.create_user(
            username="staff",
            email="staff@example.com",
            password="testpass123",
            is_staff=True,
        )
        cls.regular_user = User.objects.create_user(
            username="regular",
            email="regular@example.com",
            password="testpass123",
        )
        cls.plan = Plan.objects.create(key="main-test-plan", slug="main-test-plan")
        # Create a tenant site with the current required ownership fields.
        cls.tenant_site = Site.objects.create(
            name="Test Tenant",
            subdomain="test",
            is_main=False,
            owner=cls.regular_user,
            plan=cls.plan,
        )

    def test_main_section_settings_requires_staff(self):
        """Non-staff users cannot access main section settings."""
        client = Client()
        client.login(username="regular", password="testpass123")
        response = client.post(
            "/en/main/api/main-section-settings/",
            data=json.dumps({
                "page": "home",
                "section_key": "hero",
                "settings": {"test": True},
            }),
            content_type="application/json",
            HTTP_HOST="justcodeworks.local",
        )
        self.assertEqual(response.status_code, 403)

    def test_main_section_settings_works_for_staff(self):
        """Staff users can save main section settings."""
        client = Client()
        client.login(username="staff", password="testpass123")
        response = client.post(
            "/en/main/api/main-section-settings/",
            data=json.dumps({
                "page": "home",
                "section_key": "hero",
                "settings": {"background": {"mode": "color"}},
            }),
            content_type="application/json",
            HTTP_HOST="justcodeworks.local",
        )
        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertTrue(data.get("ok"))

        # Verify saved to MainSiteSectionSettings
        record = MainSiteSectionSettings.objects.get(page_key="home", section_key="hero")
        self.assertEqual(record.settings_json.get("background", {}).get("mode"), "color")

    def test_main_section_settings_rejected_from_tenant_host(self):
        """The main-site editor rejects tenant hosts."""
        request = RequestFactory().post(
            "/en/main/api/main-section-settings/",
            data=json.dumps({"page": "home", "section_key": "hero", "settings": {}}),
            content_type="application/json",
            HTTP_HOST="test.justcodeworks.local",
        )
        request.user = self.staff_user
        response = core_views.main_section_settings(request)
        self.assertEqual(response.status_code, 403)
        self.assertIn("main site only", json.loads(response.content).get("error", ""))


class TenantIsolationTest(TestCase):
    """Tests for tenant site isolation from main site."""

    @classmethod
    def setUpTestData(cls):
        cls.staff_user = User.objects.create_user(
            username="staff",
            email="staff@example.com",
            password="testpass123",
            is_staff=True,
        )
        cls.tenant_owner = User.objects.create_user(
            username="tenant_owner",
            email="owner@example.com",
            password="testpass123",
        )
        cls.plan = Plan.objects.create(key="tenant-test-plan", slug="tenant-test-plan")
        cls.tenant_site = Site.objects.create(
            name="Test Tenant",
            subdomain="test",
            is_main=False,
            owner=cls.tenant_owner,
            plan=cls.plan,
        )

    def test_dashboard_section_settings_rejected_from_main_host(self):
        """The tenant settings view rejects a main-site request."""
        request = RequestFactory().post(
            "/en/dashboard/api/section-settings/",
            data=json.dumps({"section_key": "hero", "settings": {}}),
            content_type="application/json",
            HTTP_HOST="justcodeworks.local",
        )
        request.user = self.staff_user
        response = core_views.dashboard_section_settings(request)
        self.assertEqual(response.status_code, 403)


class CrossContaminationTest(TestCase):
    """Tests to ensure settings don't leak between main and tenant sites."""

    @classmethod
    def setUpTestData(cls):
        cls.staff_user = User.objects.create_user(
            username="staff",
            email="staff@example.com",
            password="testpass123",
            is_staff=True,
        )
        cls.plan = Plan.objects.create(key="cross-test-plan", slug="cross-test-plan")
        cls.tenant_site = Site.objects.create(
            name="Test Tenant",
            subdomain="test",
            is_main=False,
            owner=cls.staff_user,
            plan=cls.plan,
        )

    def test_main_settings_dont_affect_tenant(self):
        """Saving main site settings doesn't affect tenant settings."""
        # Create tenant settings first
        tenant_settings = TenantHeroSettings.objects.create(
            site=self.tenant_site,
            config_json={"original": "tenant_value"},
        )

        # Save main site settings
        MainSiteSectionSettings.objects.create(
            page_key="home",
            section_key="hero",
            settings_json={"main_only": "value"},
        )

        # Verify tenant settings unchanged
        tenant_settings.refresh_from_db()
        self.assertEqual(tenant_settings.config_json.get("original"), "tenant_value")
        self.assertNotIn("main_only", tenant_settings.config_json)


class TenantResolutionIsolationTest(TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.owner_a = User.objects.create_user(username="owner-a", password="testpass123")
        cls.owner_b = User.objects.create_user(username="owner-b", password="testpass123")
        cls.staff = User.objects.create_user(
            username="tenant-staff", password="testpass123", is_staff=True
        )
        cls.plan = Plan.objects.create(key="resolution-test-plan", slug="resolution-test-plan")
        cls.tenant_a = Site.objects.create(
            name="Tenant A",
            subdomain="tenant-a",
            owner=cls.owner_a,
            plan=cls.plan,
            is_main=False,
        )
        cls.tenant_b = Site.objects.create(
            name="Tenant B",
            subdomain="tenant-b",
            owner=cls.owner_b,
            plan=cls.plan,
            is_main=False,
        )

    def test_owner_can_access_own_host_but_not_other_tenant_host(self):
        client = Client()
        client.force_login(self.owner_a)

        own_response = client.get(
            "/en/dashboard/", HTTP_HOST="tenant-a.justcodeworks.local"
        )
        other_response = client.get(
            "/en/dashboard/", HTTP_HOST="tenant-b.justcodeworks.local"
        )

        self.assertEqual(own_response.status_code, 200)
        self.assertEqual(own_response.wsgi_request.tenant, self.tenant_a)
        self.assertEqual(other_response.status_code, 403)
        self.assertEqual(other_response.wsgi_request.tenant, self.tenant_b)

    def test_anonymous_user_keeps_public_tenant_context(self):
        response = Client().get("/en/", HTTP_HOST="tenant-a.justcodeworks.local")

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.wsgi_request.tenant, self.tenant_a)

    def test_staff_context_follows_host_without_impersonation(self):
        client = Client()
        client.force_login(self.staff)

        response = client.get(
            "/en/dashboard/", HTTP_HOST="tenant-b.justcodeworks.local"
        )

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.wsgi_request.tenant, self.tenant_b)

    def test_staff_impersonation_can_select_target_and_stop_restores_host(self):
        client = Client()
        client.force_login(self.staff)
        session = client.session
        session["impersonate_tenant_id"] = self.tenant_a.id
        session.save()

        impersonated_response = client.get(
            "/en/dashboard/", HTTP_HOST="tenant-b.justcodeworks.local"
        )
        self.assertEqual(impersonated_response.status_code, 200)
        self.assertEqual(impersonated_response.wsgi_request.tenant, self.tenant_a)

        stop_response = client.get(
            "/en/control-panel/tenants/stop-impersonate/",
            HTTP_HOST="justcodeworks.local",
        )
        self.assertEqual(stop_response.status_code, 302)
        self.assertNotIn("impersonate_tenant_id", client.session)

        restored_response = client.get(
            "/en/dashboard/", HTTP_HOST="tenant-b.justcodeworks.local"
        )
        self.assertEqual(restored_response.status_code, 200)
        self.assertEqual(restored_response.wsgi_request.tenant, self.tenant_b)

    def test_ordinary_session_value_cannot_override_host(self):
        client = Client()
        client.force_login(self.owner_a)
        session = client.session
        session["impersonate_tenant_id"] = self.tenant_b.id
        session.save()

        response = client.get(
            "/en/dashboard/", HTTP_HOST="tenant-a.justcodeworks.local"
        )

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.wsgi_request.tenant, self.tenant_a)
