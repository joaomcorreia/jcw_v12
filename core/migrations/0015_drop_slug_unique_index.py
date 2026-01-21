from django.db import migrations


def drop_slug_unique_index(apps, schema_editor):
    if schema_editor.connection.vendor != "sqlite":
        return
    cursor = schema_editor.connection.cursor()
    cursor.execute("PRAGMA index_list('core_page')")
    indexes = cursor.fetchall()
    for index in indexes:
        # index_list columns: seq, name, unique, origin, partial
        name = index[1]
        unique = index[2]
        if not unique:
            continue
        cursor.execute(f"PRAGMA index_info('{name}')")
        cols = [row[2] for row in cursor.fetchall()]
        if cols == ["slug"]:
            cursor.execute(f'DROP INDEX IF EXISTS "{name}"')


class Migration(migrations.Migration):
    dependencies = [
        ("core", "0014_alter_websitetemplate_languages_and_more"),
    ]

    operations = [
        migrations.RunPython(drop_slug_unique_index, migrations.RunPython.noop),
    ]
