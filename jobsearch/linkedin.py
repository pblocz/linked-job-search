
from linkedin_api import Linkedin


from requests.cookies import RequestsCookieJar, create_cookie
from linkedin_api.cookie_repository import CookieRepository
import json
from linkedin_api.utils.helpers import get_id_from_urn
from dataclasses import dataclass, field, InitVar

from .models import JobInfo


def load_cookies() -> RequestsCookieJar:

    cookies = json.load(open('./cookies.json')) # Path of exported cookie via https://www.editthiscookie.com/

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
