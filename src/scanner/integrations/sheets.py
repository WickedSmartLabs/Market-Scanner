import gspread
import numpy as np
from google.oauth2.service_account import Credentials
from datetime import datetime, timezone
from pathlib import Path
from scanner.config.versions import FEATURE_VERSION, SCORING_VERSION

SHEET_ID = "1SvKajYPFTbAKEKuiy8UTxh0FV1pa0j9Nu7Lt67XoxaA"
CREDENTIALS_PATH = Path(__file__).parent.parent.parent.parent / "credentials" / "google_service_account.json"
SCOPES = ["https://www.googleapis.com/auth/spreadsheets", "https://www.googleapis.com/auth/drive"]
HEADERS = ["timestamp","symbol","asset_class","timeframe","confidence","status","trend_regime","volatility_regime","vpa_signal","vpa_note","options_fit","volume_ratio","body_strength","range_expansion","vwap_relationship","price","atr","stop_distance","pause_detected","volume_confirmed","feature_version","scoring_version","your_action","outcome","notes"]

def _safe(v):
    if v is None: return ""
    if isinstance(v, (bool, np.bool_)): return str(v)
    if isinstance(v, (np.integer,)): return int(v)
    if isinstance(v, (np.floating,)): return float(v)
    return v

def _get_client():
    creds = Credentials.from_service_account_file(str(CREDENTIALS_PATH), scopes=SCOPES)
    return gspread.authorize(creds)

def _get_or_create_sheet(client):
    spreadsheet = client.open_by_key(SHEET_ID)
    try:
        worksheet = spreadsheet.worksheet("Scan Log")
    except gspread.WorksheetNotFound:
        worksheet = spreadsheet.add_worksheet(title="Scan Log", rows=10000, cols=30)
    if not worksheet.row_values(1):
        worksheet.append_row(HEADERS, value_input_option="RAW")
    return worksheet

def append_scan_results(results):
    try:
        client = _get_client()
        worksheet = _get_or_create_sheet(client)
        rows = []
        timestamp = datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M:%S")
        for analysis in results:
            s = analysis["summary"]
            d = analysis["details"]
            vpa = d.get("vpa_signal") or {}
            rows.append([timestamp, _safe(s.get("symbol")), _safe(s.get("asset_class")), _safe(s.get("timeframe")), _safe(s.get("confidence")), _safe(s.get("status")), _safe(d.get("trend_regime")), _safe(d.get("volatility_regime")), _safe(vpa.get("signal")), _safe(vpa.get("vpa_note")), _safe(d.get("options_fit")), _safe(d.get("volume_ratio")), _safe(d.get("body_strength")), _safe(d.get("range_expansion")), _safe(d.get("vwap_relationship")), _safe(d.get("latest_close")), _safe(d.get("atr")), _safe(d.get("reference_stop_distance")), _safe(d.get("pause_detected")), _safe(d.get("volume_confirmed")), FEATURE_VERSION, SCORING_VERSION, "", "", ""])
        worksheet.append_rows(rows, value_input_option="RAW")
        return True
    except Exception as e:
        print(f"  Sheets sync failed: {e}")
        return False
