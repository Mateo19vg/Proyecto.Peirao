from django.db import models
from django.db.models.signals import post_delete
from django.dispatch import receiver


class Especie(models.Model):
    nombre = models.CharField(max_length=100, unique=True)
    # Condiciones óptimas para predecir si es buen momento
    temp_agua_min = models.FloatField(help_text="Temperatura mínima del agua (°C)")
    temp_agua_max = models.FloatField(help_text="Temperatura máxima del agua (°C)")
    viento_max = models.FloatField(help_text="Velocidad de viento máxima tolerable (km/h)")
    descripcion = models.TextField(blank=True)

    def __str__(self):
        return self.nombre

    class Meta:
        verbose_name_plural = "Especies"


class Spot(models.Model):
    TIPO_CHOICES = [
        ('mar', 'Mar'),
        ('rio', 'Río'),
        ('embalse', 'Embalse'),
        ('lago', 'Lago'),
    ]
    nombre = models.CharField(max_length=150)
    tipo = models.CharField(max_length=20, choices=TIPO_CHOICES, default='mar')
    latitud = models.FloatField()
    longitud = models.FloatField()
    descripcion = models.TextField(blank=True)
    es_personalizado = models.BooleanField(default=False, help_text="True si fue creado desde el mapa libre")

    def __str__(self):
        return f"{self.nombre} ({self.tipo})"


class Captura(models.Model):
    especie = models.ForeignKey(Especie, on_delete=models.CASCADE, related_name='capturas')
    spot = models.ForeignKey(Spot, on_delete=models.CASCADE, related_name='capturas')
    fecha = models.DateField()
    hora = models.TimeField()
    peso_kg = models.FloatField(null=True, blank=True)
    longitud_cm = models.FloatField(null=True, blank=True)
    # Condiciones en el momento de la captura (rellenadas automáticamente o a mano)
    temperatura_agua = models.FloatField(null=True, blank=True)
    velocidad_viento = models.FloatField(null=True, blank=True)
    notas = models.TextField(blank=True)
    foto = models.ImageField(upload_to='capturas/', null=True, blank=True)

    class Meta:
        ordering = ['-fecha', '-hora']

    def __str__(self):
        return f"{self.especie} en {self.spot} - {self.fecha}"


@receiver(post_delete, sender=Captura)
def limpiar_spot_personalizado(sender, instance, **kwargs):
    """Borra el spot personalizado si ya no tiene capturas tras eliminar una."""
    try:
        spot = instance.spot
        if spot.es_personalizado and not spot.capturas.exists():
            spot.delete()
    except Spot.DoesNotExist:
        pass