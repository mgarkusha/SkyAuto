from django.db import models


class FSms(models.Model):
    id1 = models.IntegerField(primary_key=True, blank=True, null=False)
    id2 = models.IntegerField(blank=True, null=True)
    datetime = models.FloatField(blank=True, null=True)
    datetime_d = models.IntegerField(blank=True, null=True)
    datetime_t = models.FloatField(blank=True, null=True)
    typesms = models.IntegerField(blank=True, null=True)
    state = models.IntegerField(blank=True, null=True)
    errorcode = models.IntegerField(blank=True, null=True)
    number = models.CharField(max_length=100, blank=True, null=True)
    iduser = models.IntegerField(blank=True, null=True)
    textsms = models.CharField(max_length=1000, blank=True, null=True)
    description = models.CharField(max_length=100, blank=True, null=True)
    partnumber = models.IntegerField(blank=True, null=True)
    partscount = models.IntegerField(blank=True, null=True)
    gid1 = models.IntegerField(blank=True, null=True)
    gid2 = models.IntegerField(blank=True, null=True)
    zanzara = models.IntegerField(blank=True, null=True)
    timetolive = models.FloatField(blank=True, null=True)
    server_id = models.IntegerField(blank=True, null=True)
    transferred = models.IntegerField(blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'f_sms'
        unique_together = (('id1', 'id2'),)
