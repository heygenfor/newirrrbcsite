from django.apps import AppConfig


from django.apps import AppConfig

class TransactionsConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'transactions'
    verbose_name = 'Manage Transactions'

    def ready(self):
        import transactions.signals