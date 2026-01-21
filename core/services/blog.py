from django.utils.translation import get_language


def localize_posts(posts, language_code=None):
    lang = language_code or get_language()
    for post in posts:
        post.localized_title = post.get_title(lang)
        post.localized_excerpt = post.get_excerpt(lang)
        post.localized_body = post.get_body(lang)
        if post.category_id:
            post.localized_category_name = post.category.get_name(lang)
        else:
            post.localized_category_name = ""
    return posts


def localize_categories(categories, language_code=None):
    lang = language_code or get_language()
    for category in categories:
        category.localized_name = category.get_name(lang)
    return categories
