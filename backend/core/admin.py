from django.contrib import admin
from .models import (
    Entity, Account, 
    Category, Transaction, 
    InventorySnapshot, CashFlowEvent
)

admin.site.register(Entity)
admin.site.register(Account)
admin.site.register(Category)
admin.site.register(Transaction)
admin.site.register(InventorySnapshot)
admin.site.register(CashFlowEvent)