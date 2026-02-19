from django.db import migrations, models
import django.db.models.deletion


def set_default_category(apps, schema_editor):
    Product = apps.get_model('products', 'Product')
    ProductCategory = apps.get_model('products', 'ProductCategory')
    default_category, _ = ProductCategory.objects.get_or_create(
        slug='uncategorized',
        defaults={
            'name': 'Uncategorized',
            'description': 'Default category for migrated products.',
        },
    )
    Product.objects.filter(category__isnull=True).update(category=default_category)


class Migration(migrations.Migration):
    dependencies = [
        ('products', '0003_alter_product_image'),
    ]

    operations = [
        migrations.CreateModel(
            name='ProductCategory',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=120, unique=True)),
                ('slug', models.SlugField(blank=True, max_length=140, unique=True)),
                ('description', models.TextField(blank=True)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
            ],
            options={
                'verbose_name_plural': 'Product categories',
                'ordering': ['name'],
            },
        ),
        migrations.AlterField(
            model_name='product',
            name='slug',
            field=models.SlugField(blank=True, max_length=180, unique=True),
        ),
        migrations.AddField(
            model_name='product',
            name='category',
            field=models.ForeignKey(
                blank=True,
                null=True,
                on_delete=django.db.models.deletion.CASCADE,
                related_name='products',
                to='products.productcategory',
            ),
        ),
        migrations.AddField(
            model_name='product',
            name='is_featured',
            field=models.BooleanField(db_index=True, default=False),
        ),
        migrations.RunPython(set_default_category, migrations.RunPython.noop),
        migrations.AlterField(
            model_name='product',
            name='category',
            field=models.ForeignKey(
                on_delete=django.db.models.deletion.CASCADE,
                related_name='products',
                to='products.productcategory',
            ),
        ),
        migrations.AddIndex(
            model_name='product',
            index=models.Index(fields=['is_active', 'is_featured'], name='products_pro_is_acti_153e1a_idx'),
        ),
    ]
