from django.db import models

#
#   Base de datos nuclear_properties.db
#

class Isotope(models.Model):
    symbol = models.CharField(max_length=10, unique=True)
    is_stable = models.BooleanField(null=True)
    half_life = models.FloatField(null=True, blank=True)
    A = models.IntegerField(null=True, blank=True)
    Z = models.IntegerField(null=True, blank=True)
    N = models.IntegerField(null=True, blank=True)

    def __str__(self):
        return self.symbol

    class Meta:
        managed = False # Evita que django modifique la BD
        db_table = 'isotopes'


class DecayStep(models.Model):
    isotope = models.ForeignKey(Isotope, related_name='decay_steps', on_delete=models.CASCADE)
    descendant = models.ForeignKey(Isotope, related_name='descendant_steps', on_delete=models.CASCADE)
    decay_mode = models.CharField(max_length=20)
    decay_percentage = models.FloatField()
    energy_e = models.FloatField()
    energy_a = models.FloatField()
    energy_bm = models.FloatField()
    energy_bp = models.FloatField()
    energy_g = models.FloatField()
    energy_x = models.FloatField()

    def __str__(self):
        return f"{self.isotope.symbol} -> {self.descendant.symbol} ({self.decay_mode})"

    class Meta:
        managed = False # Evita que django modifique la BD
        db_table = 'decay_steps'

#
#   Base de datos reactions_data.db
#

class Reaction(models.Model):
    id_api = models.CharField(max_length=50, db_column='id_api')
    api = models.CharField(max_length=10, db_column='api')
    author = models.CharField(max_length=100, db_column='author')
    reference = models.CharField(max_length=200, db_column='reference')
    target = models.CharField(max_length=10, db_column='target')
    product = models.CharField(max_length=10, db_column='product')
    level = models.CharField(max_length=10, db_column='level')
    projectile = models.CharField(max_length=5, db_column='projectile')
    emission = models.CharField(max_length=10, db_column='emission')
    reaction = models.CharField(max_length=50, db_column='reaction')

    def __str__(self):
        return f"{self.reaction} ({self.api})"

    class Meta:
        managed = False  # Django no administrará la tabla
        db_table = 'reactions'

class ReactionMeasurement(models.Model):
    reaction = models.ForeignKey(
        Reaction,
        related_name='measurements',
        on_delete=models.DO_NOTHING,
        db_column='reaction_id'
    )

    Energy = models.FloatField(db_column='Energy')
    Sig = models.FloatField(db_column='Sig')
    dSig = models.FloatField(db_column='dSig')

    def __str__(self):
        return f"Medición para {self.reaction_id}: E_ev={self.E_ev}"

    class Meta:
        managed = False  # No se administrará la tabla
        db_table = 'reaction_measurements'
