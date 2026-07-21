from django.contrib import admin
from .models import TaxRuleSet, TaxRule


class TaxRuleInline(admin.TabularInline):
    model = TaxRule
    extra = 1


@admin.register(TaxRuleSet)
class TaxRuleSetAdmin(admin.ModelAdmin):
    list_display = ['jurisdiction', 'effective_date', 'status', 'published_gazette_ref']
    list_filter = ['status', 'jurisdiction']
    inlines = [TaxRuleInline]


admin.site.register(TaxRule)