from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('pcm_web', '0003_alter_amalusaha_options_alter_berita_options_and_more'),
    ]

    operations = [
        migrations.AlterField(
            model_name='profilorganisasi',
            name='email',
            field=models.EmailField(blank=True, max_length=254),
        ),
    ]
