
import os
from typing import List, Dict, Optional
from google.oauth2 import service_account
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError

SCOPES = [
    "https://www.googleapis.com/auth/drive",
    "https://www.googleapis.com/auth/drive.readonly"
]

def _service():
    creds_path = os.getenv("GOOGLE_APPLICATION_CREDENTIALS")
    if not creds_path or not os.path.exists(creds_path):
        raise RuntimeError("GOOGLE_APPLICATION_CREDENTIALS no establecido o archivo inexistente")
    creds = service_account.Credentials.from_service_account_file(creds_path, scopes=SCOPES)
    return build("drive", "v3", credentials=creds, cache_discovery=False)

def search_files(keywords: List[str], folder_id: str, mime_prefix: Optional[str] = None, max_results: int = 5) -> List[Dict]:
    service = _service()
    q_parts = [f"'{folder_id}' in parents", "trashed = false"]
    for kw in keywords:
        kw = kw.replace("'", "\\'")
        q_parts.append(f"name contains '{kw}'")
    if mime_prefix:
        q_parts.append(f"mimeType contains '{mime_prefix}'")
    q = " and ".join([q_parts[0], q_parts[1]]) + (" and (" + " or ".join(q_parts[2:]) + ")" if len(q_parts) > 2 else "")
    try:
        res = service.files().list(
            q=q,
            fields="files(id, name, mimeType, webViewLink, webContentLink, iconLink, owners)",
            pageSize=max_results,
            includeItemsFromAllDrives=True,
            supportsAllDrives=True
        ).execute()
        return res.get("files", [])
    except HttpError as e:
        print("Drive search error:", e)
        return []

def ensure_anyone_reader(file_id: str) -> bool:
    """Crea permiso 'anyoneWithLink' de solo lectura si no existe. Requiere permisos de escritura."""
    try:
        service = _service()
        perm = {
            "type": "anyone",
            "role": "reader",
            "allowFileDiscovery": False
        }
        service.permissions().create(
            fileId=file_id, body=perm, fields="id", supportsAllDrives=True
        ).execute()
        return True
    except HttpError as e:
        # Si ya existe o no se puede crear, no es fatal
        print("Drive permission warn:", e)
        return False

def get_best_link(file: Dict) -> str:
    # Prefiere webContentLink (descarga) si existe; si no, usa webViewLink
    return file.get("webContentLink") or file.get("webViewLink")
