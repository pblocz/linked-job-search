
from linkedin_api import Linkedin


from requests.cookies import RequestsCookieJar, create_cookie
from linkedin_api.cookie_repository import CookieRepository
import json
from linkedin_api.utils.helpers import get_id_from_urn
from dataclasses import dataclass, field, InitVar

from .models import JobInfo

import os
from azure.storage.blob import BlobServiceClient

def read_file_from_storage_account():
    # Step 2: Retrieve the connection string from environment variables
    connection_string = os.environ["AzureWebJobsStorage"]

    # Step 3: Create a BlobServiceClient using the connection string
    blob_service_client = BlobServiceClient.from_connection_string(connection_string)

    # Step 4: Specify the container and blob name
    container_name = "config"
    blob_name = "cookies_alternative.json"

    # Create a BlobClient for the specified container and blob
    blob_client = blob_service_client.get_blob_client(container=container_name, blob=blob_name)

    try:
        # Step 5: Download the file content
        blob_data = blob_client.download_blob()
        file_content = blob_data.readall()

        # Return the file content or perform further operations
        return file_content
    except Exception as e:
        # Handle any exceptions that may occur
        # ...
        raise

# Call the function to read the file



def load_cookies() -> RequestsCookieJar:
    file_content = read_file_from_storage_account()
    cookies = json.loads(file_content) # Path of exported cookie via https://www.editthiscookie.com/

    cookie_jar = RequestsCookieJar()

    for cookie_data in cookies:
        cookie = create_cookie(
            domain=cookie_data["domain"],
            name=cookie_data["name"],
            value=cookie_data["value"],
            path=cookie_data["path"],
            secure=cookie_data["secure"],
            expires=cookie_data.get("expirationDate", None),
            rest={
                "HttpOnly": cookie_data.get("httpOnly", False),
                "SameSite": cookie_data.get("sameSite", "unspecified"),
                "HostOnly": cookie_data.get("hostOnly", False),
            }
        )
        cookie_jar.set_cookie(cookie)
    
    return cookie_jar


@dataclass
class LinkedInProcessing:
    cookie_jar: InitVar[RequestsCookieJar]
    api: Linkedin = field(init=False)

    def __post_init__(self, cookie_jar: RequestsCookieJar):
        self.api = Linkedin(None, None, cookies=cookie_jar)
    
    def search_remote_jobs(self, keywords: str, listed_offset_seconds: int = 24 * 60 * 60):
        jobs = self.api.search_jobs(keywords=keywords, remote=["2"], listed_at=listed_offset_seconds, location_name="European Union")
        return jobs

    @staticmethod
    def get_id_from_job(job):
        return get_id_from_urn(job["trackingUrn"])

    def _parse_job_info(self, job):
        job_id = self.get_id_from_job(job)
        job_info = self.api.get_job(job_id)
        return job_info

    def get_job_info(self, job) -> JobInfo:
        job_info = self._parse_job_info(job)
        return JobInfo.from_job_info(job_info)
