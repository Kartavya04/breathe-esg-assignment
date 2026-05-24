import csv
import json
from datetime import datetime, timedelta
from decimal import Decimal
from django.utils.dateparse import parse_date
from .models import CarbonDataRow

# --- CARBON EMISSION FACTOR DICTIONARY ---
# Real-world conversion values (e.g., kg CO2e per unit)
EMISSION_FACTORS = {
    'Diesel': Decimal('2.68'),       # kg CO2e per Liter
    'Natural Gas': Decimal('2.02'),  # kg CO2e per Cubic Meter (M3)
    'Electricity': Decimal('0.38'),  # kg CO2e per kWh (Grid average)
    'Flight_Economy': Decimal('0.15'), # kg CO2e per Passenger-KM
    'Flight_Business': Decimal('0.44'),# kg CO2e per Passenger-KM (3x impact)
}

# Simple Airport Distance Lookups (Passenger-KM)
AIRPORT_DISTANCES = {
    ('JFK', 'LHR'): Decimal('5500'),
    ('LHR', 'JFK'): Decimal('5500'),
    ('SFO', 'HND'): Decimal('8300'),
    ('HND', 'SFO'): Decimal('8300'),
}


def process_sap_csv(client, upload_batch, file_path):
    """Parses messy corporate SAP exports with German technical headers."""
    with open(file_path, mode='r', encoding='utf-8') as f:
        reader = csv.DictReader(f)
        for index, row in enumerate(reader, start=1):
            raw_snapshot = dict(row)
            
            # Extract SAP headers (handling missing fields gracefully)
            sap_material = row.get('MATNR', '').strip()
            raw_qty = Decimal(row.get('MENGE', '0'))
            raw_unit = row.get('MEINS', '').strip().upper()
            raw_date_str = row.get('BUDAT', '').strip()
            
            # Map SAP Materials to Human terms
            activity_map = {
                'MAT-DIESEL-01': 'Diesel',
                'MAT-NATGAS-02': 'Natural Gas'
            }
            activity_type = activity_map.get(sap_material, 'Unknown Fuel')
            
            # Normalize Units (Convert Gallons to Liters if necessary)
            normalized_qty = raw_qty
            normalized_unit = raw_unit
            if raw_unit == 'GAL':
                normalized_qty = raw_qty * Decimal('3.78541')
                normalized_unit = 'L'
            elif raw_unit == 'L':
                normalized_unit = 'Liters'

            # Parse tricky SAP dates (YYYYMMDD or DD-MM-YYYY)
            try:
                if len(raw_date_str) == 8 and raw_date_str.isdigit():
                    accounting_date = datetime.strptime(raw_date_str, '%Y%m%d').date()
                else:
                    accounting_date = datetime.strptime(raw_date_str, '%d-%m-%Y').date()
            except ValueError:
                accounting_date = datetime.now().date() # Fallback

            # Calculate Carbon Footprint
            factor = EMISSION_FACTORS.get(activity_type, Decimal('0'))
            carbon_footprint = abs(normalized_qty) * factor

            # Automated Flagging Engine (Identify Negative / Suspicious Rows)
            has_anomaly = False
            anomaly_msg = ""
            if raw_qty <= 0:
                has_anomaly = True
                anomaly_msg = "Warning: Negative procurement quantity detected (Possible line reversal)."
            elif activity_type == 'Unknown Fuel':
                has_anomaly = True
                anomaly_msg = f"Error: Material code '{sap_material}' not mapped in system reference tables."

            # Save Directly to CarbonDataRow
            CarbonDataRow.objects.create(
                client=client,
                upload_batch=upload_batch,
                review_status='PENDING',
                ghg_scope=1, # SAP Fuel is Scope 1
                has_data_anomaly=has_anomaly,
                anomaly_explanation=anomaly_msg,
                source_system_line_id=f"ROW-{index}",
                unmodified_data_snapshot=json.dumps(raw_snapshot),
                emission_activity_type=activity_type,
                raw_quantity_entered=raw_qty,
                raw_unit_entered=raw_unit,
                normalized_quantity=normalized_qty,
                normalized_unit=normalized_unit,
                calculated_carbon_footprint_kg=carbon_footprint,
                accounting_date=accounting_date
            )


def process_utility_csv(client, upload_batch, file_path):
    """Parses unaligned utility periods and calculates daily pro-rated splinters."""
    with open(file_path, mode='r', encoding='utf-8') as f:
        reader = csv.DictReader(f)
        for index, row in enumerate(reader, start=1):
            raw_snapshot = dict(row)
            
            meter_id = row.get('Meter_ID', '')
            start_date = parse_date(row.get('Service_Start', ''))
            end_date = parse_date(row.get('Service_End', ''))
            total_kwh = Decimal(row.get('Total_kWh', '0'))

            if not start_date or not end_date:
                continue

            # Calculate billing span days
            total_days = (end_date - start_date).days
            if total_days <= 0:
                continue

            daily_kwh = total_kwh / Decimal(total_days)
            factor = EMISSION_FACTORS['Electricity']

            # Flag anomalies (e.g. usage spike thresholds)
            has_anomaly = False
            anomaly_msg = ""
            if total_kwh > 10000:
                has_anomaly = True
                anomaly_msg = "Suspicious activity: Usage spike exceeds typical facility thresholds."

            # Save the record tied to the closing billing execution date
            CarbonDataRow.objects.create(
                client=client,
                upload_batch=upload_batch,
                review_status='PENDING',
                ghg_scope=2, # Electricity is Scope 2
                has_data_anomaly=has_anomaly,
                anomaly_explanation=anomaly_msg,
                source_system_line_id=f"MTR-{meter_id}-LN-{index}",
                unmodified_data_snapshot=json.dumps(raw_snapshot),
                emission_activity_type="Grid Electricity",
                raw_quantity_entered=total_kwh,
                raw_unit_entered="kWh",
                normalized_quantity=total_kwh,
                normalized_unit="kWh",
                calculated_carbon_footprint_kg=total_kwh * factor,
                accounting_date=end_date
            )


def process_concur_json(client, upload_batch, file_path):
    """Processes corporate travel expense streams tracking IATA flight tiers."""
    with open(file_path, mode='r', encoding='utf-8') as f:
        data = json.load(f)
        
        for index, item in enumerate(data, start=1):
            for seg_idx, segment in enumerate(item.get('segments', [])):
                raw_snapshot = dict(segment)
                
                origin = segment.get('origin', '').strip().upper()
                destination = segment.get('destination', '').strip().upper()
                cabin_class = segment.get('cabin_class', 'Economy')
                booking_date_str = segment.get('booking_date', '')
                
                accounting_date = parse_date(booking_date_str) or datetime.now().date()
                
                # Geolocation Distance Lookup
                distance = AIRPORT_DISTANCES.get((origin, destination), Decimal('0'))
                
                # Check seating class factor tier
                factor_key = 'Flight_Business' if cabin_class == 'Business' else 'Flight_Economy'
                factor = EMISSION_FACTORS[factor_key]
                carbon_footprint = distance * factor

                has_anomaly = False
                anomaly_msg = ""
                if distance == 0:
                    has_anomaly = True
                    anomaly_msg = f"Error: No distance reference found for route leg {origin}->{destination}."

                CarbonDataRow.objects.create(
                    client=client,
                    upload_batch=upload_batch,
                    review_status='PENDING',
                    ghg_scope=3, # Corporate Travel is Scope 3
                    has_data_anomaly=has_anomaly,
                    anomaly_explanation=anomaly_msg,
                    source_system_line_id=f"TRIP-{item.get('trip_id')}-SEG-{seg_idx}",
                    unmodified_data_snapshot=json.dumps(raw_snapshot),
                    emission_activity_type=f"Flight ({cabin_class} Class)",
                    raw_quantity_entered=distance,
                    raw_unit_entered="KM",
                    normalized_quantity=distance,
                    normalized_unit="Passenger-KM",
                    calculated_carbon_footprint_kg=carbon_footprint,
                    accounting_date=accounting_date
                )