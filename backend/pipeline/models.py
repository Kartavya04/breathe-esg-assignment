from django.db import models
from django.contrib.auth.models import User
from django.core.exceptions import ValidationError

class CompanyClient(models.Model):
    """Isolates data for different corporate clients (Multi-tenancy)."""
    company_name = models.CharField(max_length=255)
    joined_date = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.company_name


class DataUploadBatch(models.Model):
    """Tracks every individual file upload or API sync event."""
    SOURCE_SYSTEM_CHOICES = [
        ('SAP', 'SAP Procurement ERP'),
        ('UTILITY', 'Utility Portal Export'),
        ('CONCUR', 'Concur Corporate Travel'),
    ]
    client = models.ForeignKey(CompanyClient, on_delete=models.CASCADE)
    source_system = models.CharField(max_length=15, choices=SOURCE_SYSTEM_CHOICES)
    uploaded_at = models.DateTimeField(auto_now_add=True)
    uploaded_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True)
    original_file_name = models.CharField(max_length=255)

    def __str__(self):
        return f"{self.source_system} Upload ({self.original_file_name}) - {self.uploaded_at.date()}"


class CarbonDataRow(models.Model):
    """
    Stores individual transaction lines. Decouples raw inputs 
    from the standardized values reviewed by the analyst.
    """
    REVIEW_STATUS_CHOICES = [
        ('PENDING', 'Pending Analyst Review'),
        ('APPROVED', 'Approved & Locked for Audit'),
    ]
    
    GREENHOUSE_GAS_SCOPE_CHOICES = [
        (1, 'Scope 1 (Direct Emissions - e.g., Fuel)'),
        (2, 'Scope 2 (Indirect Emissions - e.g., Electricity)'),
        (3, 'Scope 3 (Value Chain - e.g., Business Travel)'),
    ]

    client = models.ForeignKey(CompanyClient, on_delete=models.CASCADE)
    upload_batch = models.ForeignKey(DataUploadBatch, on_delete=models.CASCADE)
    
    # Workflow & Audit Controls
    review_status = models.CharField(max_length=15, choices=REVIEW_STATUS_CHOICES, default='PENDING')
    ghg_scope = models.IntegerField(choices=GREENHOUSE_GAS_SCOPE_CHOICES)
    is_finalized_and_locked = models.BooleanField(default=False)
    
    # Automated Flagging Engine
    has_data_anomaly = models.BooleanField(default=False)
    anomaly_explanation = models.TextField(blank=True, null=True)

    # Lineage / Original Source Tracking
    source_system_line_id = models.CharField(max_length=100) # Row index number or unique API ID
    unmodified_data_snapshot = models.TextField()          # Safe for SQLite on Windows
    
    # Cleaned & Calculated Fields for the Analyst View
    emission_activity_type = models.CharField(max_length=100) # e.g., "Diesel", "Grid Electricity", "Flight"
    raw_quantity_entered = models.DecimalField(max_digits=15, decimal_places=4)
    raw_unit_entered = models.CharField(max_length=20)        # e.g., "GAL", "M3", "kWh"
    
    normalized_quantity = models.DecimalField(max_digits=15, decimal_places=4)
    normalized_unit = models.CharField(max_length=20)         # Standardized to "Liters", "kWh", "Passenger-KM"
    calculated_carbon_footprint_kg = models.DecimalField(max_digits=15, decimal_places=4)
    
    accounting_date = models.DateField()                       # The target date this emission applies to

    def save(self, *args, **kwargs):
        # Database level safety lock: Freeze the data row completely if it is approved
        if self.pk:
            previous_state = CarbonDataRow.objects.get(pk=self.pk)
            if previous_state.is_finalized_and_locked:
                raise ValidationError("This record has been officially signed off and locked. Modifying it is prohibited.")
        super().save(*args, **kwargs)


class AnalystChangeLog(models.Model):
    """Maintains a bulletproof timeline of human overrides for the auditors."""
    data_row = models.ForeignKey(CarbonDataRow, on_delete=models.CASCADE, related_name='change_logs')
    reviewed_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True)
    action_timestamp = models.DateTimeField(auto_now_add=True)
    action_performed = models.CharField(max_length=50, default="MANUAL_EDIT") # MANUAL_EDIT, AUDIT_SIGN_OFF
    audit_trail_details = models.TextField()                                 # Safe for SQLite on Windows