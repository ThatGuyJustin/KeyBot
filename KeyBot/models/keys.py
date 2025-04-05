from peewee import IntegerField, TextField, BigIntegerField, DateTimeField

from KeyBot.database import SQLiteBase


@SQLiteBase.register
class FreeKey(SQLiteBase):
    class Meta:
        table_name = "free_keys"

    id = IntegerField(primary_key=True)
    message = TextField(null=True)
    title = TextField()
    platform = TextField()
    key = TextField()
    submitter = BigIntegerField()
    claimer = BigIntegerField(null=True)
    submitted_at = DateTimeField(null=False)
    claimed_at = DateTimeField(null=True)