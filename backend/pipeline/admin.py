# pipeline/admin.py
from django.contrib import admin
from .models import CompanyClient, DataUploadBatch, CarbonDataRow

# 🌟 In teeno models ko admin panel par register kar rahe hain taaki wahan dikhein
@admin.register(CompanyClient)
class CompanyClientAdmin(admin.ModelAdmin):
    list_display = ('id', 'company_name', 'created_at')
    search_fields = ('company_name',)

@admin.register(DataUploadBatch)
class DataUploadBatchAdmin(admin.ModelAdmin):
    list_display = ('id', 'client', 'source_system', 'original_file_name', 'uploaded_at')
    list_filter = ('source_system', 'uploaded_at')

@admin.register(CarbonDataRow)
class CarbonDataRowAdmin(admin.ModelAdmin):
    list_display = ('id', 'source_system_line_id', 'emission_activity_type', 'ghg_scope', 'normalized_quantity', 'normalized_unit', 'calculated_carbon_footprint_kg', 'review_status', 'is_finalized_and_locked')
    list_filter = ('review_status', 'ghg_scope', 'has_data_anomaly', 'is_finalized_and_locked')
    search_fields = ('source_system_line_id', 'emission_activity_type')