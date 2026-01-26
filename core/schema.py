from django.conf import settings

from core.seo_caps import get_seo_caps
from core.seo_utils import build_language_url_for_path
from core.services.visibility import get_seo_target_cities
from core.visibility_rules import SEO_TIER_COUNTRY, SEO_TIER_EU, SEO_TIER_LOCAL


def _absolute_url(request, value):
    if not value:
        return None
    if isinstance(value, str) and (value.startswith("http://") or value.startswith("https://")):
        return value
    return request.build_absolute_uri(value)


def _resolve_logo_url(request, logo):
    if not logo:
        return None
    url = getattr(logo, "url", None) or logo
    return _absolute_url(request, url)


def _clean_list(values):
    if not values:
        return []
    cleaned = []
    for value in values:
        if isinstance(value, str):
            value = value.strip()
        if value:
            cleaned.append(value)
    return cleaned


def _get_page_title(page, language_code):
    if not page:
        return ""
    if hasattr(page, "safe_translation_getter"):
        return page.safe_translation_getter("title", any_language=True) or ""
    title = getattr(page, "title", "")
    if isinstance(title, dict):
        return title.get(language_code) or title.get("en") or ""
    return title or ""


def _is_blog_post(page):
    return all(
        hasattr(page, attr)
        for attr in ("slug", "published_at", "category", "get_title", "get_excerpt")
    )


def _collect_service_items(page, language_code):
    items = []
    if not page or not hasattr(page, "sections"):
        return items
    for section in page.sections.all():
        key = (section.key or "").split(".")[-1]
        if key != "services":
            continue
        content = getattr(section, "content", None)
        data = content.config_json if content else {}
        for item in data.get("items", []):
            title = (item.get("title") or "").strip()
            description = (item.get("description") or "").strip()
            if title:
                items.append({"name": title, "description": description})
    return items


def _collect_faq_items(page, language_code):
    items = []
    if not page or not hasattr(page, "sections"):
        return items
    for section in page.sections.all():
        key = (section.key or "").split(".")[-1]
        content = getattr(section, "content", None)
        data = content.config_json if content else {}
        faq_entries = []
        if key == "faq" and data.get("faq_items"):
            faq_entries = data.get("faq_items") or []
        elif "faq" in key and content:
            heading = getattr(content, "heading", "") or ""
            body = getattr(content, "body", "") or ""
            if heading:
                faq_entries = [{"heading": heading, "body": body}]
        for entry in faq_entries:
            question = (entry.get("heading") or "").strip()
            answer = (entry.get("body") or "").strip()
            if question and answer:
                items.append({"question": question, "answer": answer})
    return items


def _build_breadcrumbs(request, page, language_code):
    path = (request.path or "/").strip("/")
    segments = path.split("/") if path else []
    languages = {code for code, _name in settings.LANGUAGES}
    if segments and segments[0] in languages:
        segments = segments[1:]
    crumbs = [{"name": "Home", "path": "/"}]
    if segments:
        current_path = ""
        for segment in segments:
            current_path = f"{current_path}/{segment}"
            crumbs.append({"name": segment, "path": f"{current_path}/"})
    if page:
        title = _get_page_title(page, language_code)
        if title and crumbs:
            crumbs[-1]["name"] = title
    breadcrumb_items = []
    for idx, crumb in enumerate(crumbs, start=1):
        url = build_language_url_for_path(request, language_code, crumb["path"])
        label = " ".join(crumb["name"].split("-")).title()
        breadcrumb_items.append(
            {"@type": "ListItem", "position": idx, "name": label, "item": url}
        )
    return {
        "@context": "https://schema.org",
        "@type": "BreadcrumbList",
        "itemListElement": breadcrumb_items,
    }


def build_schema(site, site_settings, request, page=None):
    business_name = (getattr(site_settings, "business_name", "") or "").strip()
    if not business_name and site:
        business_name = site.name

    phone = (getattr(site_settings, "phone", "") or "").strip()
    email = (getattr(site_settings, "email", "") or "").strip()
    address_line1 = (getattr(site_settings, "address_line1", "") or "").strip()
    address_line2 = (getattr(site_settings, "address_line2", "") or "").strip()
    postal_code = (getattr(site_settings, "postal_code", "") or "").strip()
    city = (getattr(site_settings, "city", "") or "").strip()
    country = (getattr(site_settings, "country", "") or "").strip()
    logo_url = _resolve_logo_url(request, getattr(site_settings, "logo", None))

    socials = getattr(site_settings, "socials", None)
    if isinstance(socials, dict):
        socials = list(socials.values())
    socials = _clean_list(socials)

    base_url = request.build_absolute_uri("/")

    organization = {
        "@context": "https://schema.org",
        "@type": "Organization",
        "name": business_name,
        "url": base_url,
    }
    if logo_url:
        organization["logo"] = logo_url
    if email:
        organization["email"] = email
    if phone:
        organization["telephone"] = phone
    if socials:
        organization["sameAs"] = socials

    website = {
        "@context": "https://schema.org",
        "@type": "WebSite",
        "name": business_name,
        "url": base_url,
    }

    caps = get_seo_caps(request=request, tenant=site)
    seo_tier = caps["tier"]

    target_cities = []
    if site:
        target_cities = get_seo_target_cities(site)

    if seo_tier == SEO_TIER_LOCAL and target_cities:
        selected_city = target_cities[0].get("city") or ""
        selected_country = target_cities[0].get("country") or ""
        if selected_city:
            city = " ".join(selected_city.split("-")).title()
        if selected_country:
            country = selected_country.upper()

    has_address = any([address_line1, address_line2, postal_code, city, country])
    has_contact = any([phone, email, has_address])
    local_business = None
    if has_contact:
        local_business = {
            "@context": "https://schema.org",
            "@type": "LocalBusiness",
            "name": business_name,
            "url": base_url,
        }
        if logo_url:
            local_business["image"] = logo_url
            local_business["logo"] = logo_url
        if phone:
            local_business["telephone"] = phone
        if email:
            local_business["email"] = email
        if has_address:
            street_parts = [part for part in [address_line1, address_line2] if part]
            local_business["address"] = {
                "@type": "PostalAddress",
                "streetAddress": ", ".join(street_parts),
            }
            if postal_code:
                local_business["address"]["postalCode"] = postal_code
            if city:
                local_business["address"]["addressLocality"] = city
            if country:
                local_business["address"]["addressCountry"] = country

    schema = [organization, website]
    if local_business and caps["schema_level"] != "none":
        schema.append(local_business)
        if target_cities:
            areas = []
            for entry in target_cities:
                city_slug = entry.get("city") or ""
                country_code = entry.get("country") or ""
                if not city_slug:
                    continue
                label_city = " ".join(city_slug.split("-")).title()
                label_country = country_code.upper() if country_code else ""
                if label_country:
                    areas.append(f"{label_city}, {label_country}")
                else:
                    areas.append(label_city)
            if areas:
                local_business["areaServed"] = areas
    if seo_tier == SEO_TIER_COUNTRY and target_cities and caps["schema_level"] != "none":
        lang = getattr(request, "LANGUAGE_CODE", None) or "en"
        items = []
        for idx, entry in enumerate(target_cities, start=1):
            country_code = entry.get("country")
            city_slug = entry.get("city")
            if not country_code or not city_slug:
                continue
            url = build_language_url_for_path(
                request,
                lang,
                f"/locations/{country_code}/{city_slug}/",
            )
            items.append({"@type": "ListItem", "position": idx, "url": url})
        if items:
            schema.append(
                {
                    "@context": "https://schema.org",
                    "@type": "ItemList",
                    "itemListElement": items,
                }
            )
    if caps["schema_level"] == "full":
        language_code = getattr(request, "LANGUAGE_CODE", None) or "en"
        if _is_blog_post(page):
            headline = page.get_title(language_code) or page.slug
            description = page.get_excerpt(language_code) or ""
            date_published = page.published_at.isoformat() if page.published_at else None
            date_modified = page.updated_at.isoformat() if getattr(page, "updated_at", None) else None
            image_url = _absolute_url(request, getattr(page.featured_image, "url", None)) if getattr(page, "featured_image", None) else None
            article = {
                "@context": "https://schema.org",
                "@type": "Article",
                "headline": headline,
                "description": description,
                "mainEntityOfPage": request.build_absolute_uri(request.path),
                "author": {"@type": "Organization", "name": business_name},
                "publisher": {
                    "@type": "Organization",
                    "name": business_name,
                },
            }
            if logo_url:
                article["publisher"]["logo"] = {"@type": "ImageObject", "url": logo_url}
            if date_published:
                article["datePublished"] = date_published
            if date_modified:
                article["dateModified"] = date_modified
            if image_url:
                article["image"] = image_url
            schema.append(article)
        else:
            service_items = _collect_service_items(page, language_code)
            if service_items:
                area_served = None
                if target_cities:
                    area_served = []
                    for entry in target_cities:
                        city_slug = entry.get("city") or ""
                        country_code = entry.get("country") or ""
                        if not city_slug:
                            continue
                        label_city = " ".join(city_slug.split("-")).title()
                        label_country = country_code.upper() if country_code else ""
                        if label_country:
                            area_served.append(f"{label_city}, {label_country}")
                        else:
                            area_served.append(label_city)
                for item in service_items:
                    service_schema = {
                        "@context": "https://schema.org",
                        "@type": "Service",
                        "name": item.get("name"),
                        "description": item.get("description"),
                        "provider": {"@type": "Organization", "name": business_name},
                    }
                    if area_served:
                        service_schema["areaServed"] = area_served
                    schema.append(service_schema)
            faq_items = _collect_faq_items(page, language_code)
            if faq_items:
                schema.append(
                    {
                        "@context": "https://schema.org",
                        "@type": "FAQPage",
                        "mainEntity": [
                            {
                                "@type": "Question",
                                "name": entry["question"],
                                "acceptedAnswer": {
                                    "@type": "Answer",
                                    "text": entry["answer"],
                                },
                            }
                            for entry in faq_items
                        ],
                    }
                )
        breadcrumbs = _build_breadcrumbs(request, page, language_code)
        if breadcrumbs:
            schema.append(breadcrumbs)
    return schema
