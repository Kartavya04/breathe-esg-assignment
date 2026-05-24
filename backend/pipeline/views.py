from rest_framework import generics, status
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.parsers import MultiPartParser
from django.contrib.auth.models import User
from decimal import Decimal
import csv
import io

# Import your advanced data model structures
from .models import CompanyClient, DataUploadBatch, CarbonDataRow
from .serializers import CarbonDataRowSerializer

# 1. INGEST & AUTOMATICALLY PROCESS UPLOADED ESG DATASET
class DataIngestionAPIView(APIView):
    parser_classes = [MultiPartParser]

    def post(self, request, *args, **kwargs):
        source_system = request.data.get('source_system', 'SAP')
        file_obj = request.data.get('file')

        if not file_obj:
            return Response({"error": "No data file provided."}, status=status.HTTP_400_BAD_REQUEST)

        try:
            # A. SETUP MANDATORY COMPLIANCE ENTITIES FOR MULTI-TENANCY
            client_tenant, _ = CompanyClient.objects.get_or_create(
                company_name="BreatheESG Primary Enterprise Tenant"
            )
            
            # Grab a default user account to attribute the upload lineage to
            fallback_user = User.objects.filter(is_superuser=True).first()

            # B. CREATE REUSABLE AUDIT BATCH LINEAGE RECORD
            upload_batch = DataUploadBatch.objects.create(
                client=client_tenant,
                source_system=source_system,
                uploaded_by=fallback_user,
                original_file_name=getattr(file_obj, 'name', 'raw_ingestion_feed.csv')
            )

            # C. EXTRACT AND PARSE STREAM DATA
            csv_file = io.TextIOWrapper(file_obj.file, encoding='utf-8')
            reader = csv.DictReader(csv_file)
            
            rows_created = 0
            for row in reader:
                raw_quantity = float(row.get('quantity', 0))
                activity_type = row.get('activity_type', 'Unknown').strip()
                raw_unit = row.get('unit', 'UNKN').strip()
                
                # Default baseline calculation variables 
                emissions_modifier = 1.0
                normalized_unit = raw_unit
                ghg_scope = 1
                has_anomaly = False
                anomaly_explanation = ""

                # Business normalization rules validation engine
                if "Diesel" in activity_type:
                    emissions_modifier = 2.68  
                    normalized_unit = "Liters"
                    ghg_scope = 1
                elif "Natural Gas" in activity_type:
                    emissions_modifier = 2.02  
                    normalized_unit = "M3"
                    ghg_scope = 1
                elif "Electricity" in activity_type:
                    emissions_modifier = 0.85  
                    normalized_unit = "kWh"
                    ghg_scope = 2
                else:
                    has_anomaly = True
                    anomaly_explanation = f"Error: Material item type '{activity_type}' not mapped in pipeline system tables."
                    emissions_modifier = 0.0

                if raw_quantity < 0:
                    has_anomaly = True
                    anomaly_explanation = "Warning: Negative procurement quantity balance reversal line flags automated anomaly indicator check."

                calculated_footprint = max(0.0, raw_quantity * emissions_modifier)

                # D. COMMIT ROW LEVEL DATA OBJECT MAP DIRECTLY TO YOUR TARGET SCHEMA FIELDS
                CarbonDataRow.objects.create(
                    client=client_tenant,
                    upload_batch=upload_batch,
                    review_status='PENDING',
                    ghg_scope=ghg_scope,
                    is_finalized_and_locked=False,
                    has_data_anomaly=has_anomaly,
                    anomaly_explanation=anomaly_explanation,
                    source_system_line_id=row.get('line_id', 'UNKNOWN_ID'),
                    unmodified_data_snapshot=str(dict(row)), # Safe string proof for audit trials
                    emission_activity_type=activity_type,
                    raw_quantity_entered=Decimal(str(raw_quantity)),
                    raw_unit_entered=raw_unit,
                    normalized_quantity=Decimal(str(raw_quantity)),
                    normalized_unit=normalized_unit,
                    calculated_carbon_footprint_kg=Decimal(str(calculated_footprint)),
                    accounting_date=row.get('date', '2026-01-01')
                )
                rows_created += 1

            return Response({
                "message": f"Successfully parsed and processed {source_system} pipeline dataset batch ({rows_created} rows)."
            }, status=status.HTTP_201_CREATED)

        except Exception as e:
            return Response({"error": f"Dataset extraction pipeline failed: {str(e)}"}, status=status.HTTP_400_BAD_REQUEST)


# 2. RENDER BALANCES WAITING IN PENDING OPERATIONS QUEUE
class AnalystReviewQueueView(generics.ListAPIView):
    serializer_class = CarbonDataRowSerializer

    def get_queryset(self):
        return CarbonDataRow.objects.filter(review_status='PENDING').order_by('-id')


# 3. CHRONOLOGICAL VERIFIED APPROVED LEDGER WORKSPACE
class ApprovedLedgerView(generics.ListAPIView):
    serializer_class = CarbonDataRowSerializer

    def get_queryset(self):
        return CarbonDataRow.objects.filter(review_status='APPROVED').order_by('-id')


# 4. MUTATE OPERATIONS PROCESSING WORKFLOW STATE CONTROL ACTION
class ProcessRowActionView(APIView):
    def post(self, request, pk, *args, **kwargs):
        try:
            row = CarbonDataRow.objects.get(pk=pk)
            action = request.data.get('action')

            if action == 'APPROVE':
                # Shift state AND trigger your secure model-level immutable sign-off lock!
                row.review_status = 'APPROVED'
                row.is_finalized_and_locked = True
                row.save()
                return Response({"message": f"Line record {pk} verified and locked to ledger balances successfully."}, status=status.HTTP_200_OK)
            else:
                return Response({"error": "Unsupported audit workflow operation signature."}, status=status.HTTP_400_BAD_REQUEST)
                
        except CarbonDataRow.DoesNotExist:
            return Response({"error": "Target sequence reference identifier not found."}, status=status.HTTP_404_NOT_FOUND)