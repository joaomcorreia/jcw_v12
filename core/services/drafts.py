from django.utils import timezone


def ensure_draft_site(request):
    draft = request.session.get("draft_site")
    if draft:
        return draft
    draft = {
        "business_name": "",
        "business_type": "",
        "city": "",
        "country": "",
        "preferred_language": request.LANGUAGE_CODE,
        "selected_template_key": "",
        "created_at": timezone.now().isoformat(),
    }
    request.session["draft_site"] = draft
    request.session.modified = True
    return draft


def get_draft_site(request):
    return request.session.get("draft_site")


def save_draft_site(request, draft):
    request.session["draft_site"] = draft
    request.session.modified = True


def clear_draft_site(request):
    if "draft_site" in request.session:
        del request.session["draft_site"]
        request.session.modified = True
