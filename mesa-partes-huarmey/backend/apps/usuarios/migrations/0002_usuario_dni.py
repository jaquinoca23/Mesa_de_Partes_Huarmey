from django.core.validators import RegexValidator
from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [('usuarios', '0001_initial')]

    operations = [
        migrations.AddField(
            model_name='usuario',
            name='dni',
            field=models.CharField(
                max_length=8, unique=True, null=True, blank=True,
                validators=[RegexValidator(r'^[0-9]{8}$', 'El DNI debe contener exactamente 8 dígitos.')],
            ),
        ),
    ]
