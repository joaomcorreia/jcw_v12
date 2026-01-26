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

from django.test import TestCase, Client, override_settings
from django.urls import reverse
from django.contrib.auth import get_user_model
from core.models import Site, MainSiteSectionSettings, TenantHeroSettings
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
        # Create a tenant site
        cls.tenant_site = Site.objects.create(
            name="Test Tenant",
            subdomain="test",
            is_main=False,
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
        """Main section settings endpoint rejects requests from tenant hosts."""
        client = Client()
        client.login(username="staff", password="testpass123")
        response = client.post(
            "/en/main/api/main-section-settings/",
            data=json.dumps({
                "page": "home",
                "section_key": "hero",
                "settings": {"test": True},
            }),
            content_type="application/json",
            HTTP_HOST="test.justcodeworks.local",  # Tenant host
        )
        self.assertEqual(response.status_code, 403)
        data = response.json()
        self.assertIn("main site only", data.get("error", ""))


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
        cls.tenant_site = Site.objects.create(
            name="Test Tenant",
            subdomain="test",
            is_main=False,
            owner=cls.tenant_owner,
        )

    def test_dashboard_section_settings_rejected_from_main_host(self):
        """Dashboard section settings endpoint rejects requests from main host."""
        client = Client()
        client.login(username="staff", password="testpass123")
        response = client.post(
            "/en/dashboard/api/section-settings/",
            data=json.dumps({
                "section_key": "hero",
                "settings": {"test": True},
            }),
            content_type="application/json",
            HTTP_HOST="justcodeworks.local",  # Main host
        )
        # Should be 403 because this is main site host
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
        cls.tenant_site = Site.objects.create(
            name="Test Tenant",
            subdomain="test",
            is_main=False,
            owner=cls.staff_user,
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
