"""Environment configuration — no hardcoded credentials."""

import os
from dataclasses import dataclass

from dotenv import load_dotenv

_PROJECT_ROOT = os.path.dirname(
    os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
)
load_dotenv(os.path.join(_PROJECT_ROOT, ".env"), override=True)

ZOHO_API_BASES = {
    "US": "https://books.zoho.com/api/v3",
    "EU": "https://books.zoho.eu/api/v3",
    "IN": "https://books.zoho.in/api/v3",
    "AU": "https://books.zoho.com.au/api/v3",
    "JP": "https://books.zoho.jp/api/v3",
    "CA": "https://books.zoho.ca/api/v3",
    "UK": "https://books.zoho.uk/api/v3",
    "SA": "https://books.zoho.sa/api/v3",
}

ZOHO_TOKEN_URLS = {
    "US": "https://accounts.zoho.com/oauth/v2/token",
    "EU": "https://accounts.zoho.eu/oauth/v2/token",
    "IN": "https://accounts.zoho.in/oauth/v2/token",
    "AU": "https://accounts.zoho.com.au/oauth/v2/token",
    "JP": "https://accounts.zoho.jp/oauth/v2/token",
    "CA": "https://accounts.zoho.ca/oauth/v2/token",
    "UK": "https://accounts.zoho.uk/oauth/v2/token",
    "SA": "https://accounts.zoho.sa/oauth/v2/token",
}


@dataclass(frozen=True)
class Settings:
    bp_license_key: str
    bp_api_url: str
    zoho_client_id: str
    zoho_client_secret: str
    zoho_access_token: str
    zoho_refresh_token: str
    zoho_organization_id: str
    zoho_org_name: str
    zoho_org_address: str
    zoho_webhook_token: str
    zoho_region: str
    host: str
    port: int
    skip_token_verify: bool
    failed_queue_dir: str

    @property
    def zoho_api_base(self) -> str:
        region = self.zoho_region.upper()
        return ZOHO_API_BASES.get(region, ZOHO_API_BASES["US"])

    @property
    def zoho_token_url(self) -> str:
        region = self.zoho_region.upper()
        return ZOHO_TOKEN_URLS.get(region, ZOHO_TOKEN_URLS["US"])


def get_settings() -> Settings:
    root = _PROJECT_ROOT
    return Settings(
        bp_license_key=os.getenv("BP_LICENSE_KEY", "").strip(),
        bp_api_url=os.getenv(
            "BP_API_URL", "https://branchlesspay.com/api/v1/anchor"
        ).rstrip("/"),
        zoho_client_id=os.getenv("ZOHO_CLIENT_ID", "").strip(),
        zoho_client_secret=os.getenv("ZOHO_CLIENT_SECRET", "").strip(),
        zoho_access_token=os.getenv("ZOHO_ACCESS_TOKEN", "").strip(),
        zoho_refresh_token=os.getenv("ZOHO_REFRESH_TOKEN", "").strip(),
        zoho_organization_id=os.getenv("ZOHO_ORGANIZATION_ID", "").strip(),
        zoho_org_name=os.getenv("ZOHO_ORG_NAME", "").strip(),
        zoho_org_address=os.getenv("ZOHO_ORG_ADDRESS", "").strip(),
        zoho_webhook_token=os.getenv("ZOHO_WEBHOOK_TOKEN", "").strip(),
        zoho_region=os.getenv("ZOHO_REGION", "US").strip().upper(),
        host=os.getenv("HOST", "127.0.0.1"),
        port=int(os.getenv("PORT", "8080")),
        skip_token_verify=os.getenv("ZOHO_SKIP_TOKEN_VERIFY", "0").strip()
        in ("1", "true", "yes"),
        failed_queue_dir=os.getenv(
            "FAILED_QUEUE_DIR", os.path.join(root, "data", "failed_queue")
        ),
    )
