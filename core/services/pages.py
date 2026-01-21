from django.db.models import Prefetch

from django.utils.translation import get_language

from core.models import Page, PageSection, RightSidebarPanel, SectionContent


def get_page_with_sections(slug):
    page = (
        Page.objects.filter(slug=slug, is_active=True, site__isnull=True)
        .prefetch_related(
            "translations",
            Prefetch(
                "sections",
                queryset=PageSection.objects.filter(is_visible=True)
                .prefetch_related("content__translations")
                .order_by("order", "id"),
            ),
            "sections__content__translations",
        )
        .first()
    )
    sections_by_key = {}
    if page:
        sections_by_key = {section.key: section for section in page.sections.all()}
    return page, sections_by_key


def get_sidebar_panel(page_slug):
    if page_slug:
        panel = (
            RightSidebarPanel.objects.filter(
                page__slug=page_slug,
                page__site__isnull=True,
                is_enabled=True,
            )
            .prefetch_related("translations")
            .first()
        )
        if panel:
            panel.set_current_language(get_language())
            return panel

    panel = (
        RightSidebarPanel.objects.filter(page__isnull=True, is_enabled=True)
        .prefetch_related("translations")
        .first()
    )
    if panel:
        panel.set_current_language(get_language())
    return panel
