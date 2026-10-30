from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [('documentos', '0002_initial')]
    operations = [migrations.AddField(model_name='adjunto', name='es_principal', field=models.BooleanField(default=False))]
