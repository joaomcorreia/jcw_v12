from django.utils import timezone

from core.models import Feature, Plan, PlanFeature, Subscription


def get_enabled_features_for_plan(plan_key):
    features = Feature.objects.all()
    enabled_map = {feature.key: False for feature in features}

    if not plan_key:
        return enabled_map

    plan = Plan.objects.filter(key=plan_key, is_active=True).first()
    if not plan:
        return enabled_map

    plan_features = (
        PlanFeature.objects.filter(plan=plan, is_enabled=True)
        .select_related("feature")
    )
    for plan_feature in plan_features:
        enabled_map[plan_feature.feature.key] = True

    return enabled_map


def get_active_subscription():
    return (
        Subscription.objects.filter(status=Subscription.STATUS_ACTIVE)
        .order_by("-started_at", "-id")
        .first()
    )


def resolve_active_plan(site=None):
    if site is not None:
        site_plan = getattr(site, "plan", None)
        if site_plan:
            return site_plan

    subscription = get_active_subscription()
    if subscription:
        return subscription.plan

    plan = Plan.objects.filter(key="growth", is_active=True).first()
    if plan:
        return plan
    return Plan.objects.filter(key="starter", is_active=True).first()
