import pytest

import os

from jobsearch.openai import job_summary_openai
from jobsearch.models import SummaryJob


def test_openai_query():
    job_info_summary = job_summary_openai(TEST_JOB).to_dataclass()

    print(job_info_summary.to_dict())
    assert isinstance(job_info_summary, SummaryJob)


TEST_JOB = '''
Captain Blackbeard's Crew is a renowned group of swashbuckling pirates operating in the Mediterranean Sea. We specialize in high-seas adventures, treasure hunts, and thrilling escapades. Our crew is known for its camaraderie, daring spirit, and love for the open waters.

Are you ready to embark on a daring career as a Quartermaster Pirate in the Mediterranean? Join our crew and be part of a legendary pirate adventure! As the Quartermaster, you will play a crucial role in maintaining order and ensuring the smooth operation of our pirate ship.

Key Responsibilities:

Crew Management: As the Quartermaster, you'll oversee the crew, assigning duties, and maintaining discipline on board. Your leadership ensures that everyone is working together efficiently.

Supplies and Provisions: Manage the ship's supplies, including food, water, and ammunition. Ensure that the crew has everything they need for the voyage.

Navigation: Assist the ship's navigator in plotting courses and navigating the treacherous Mediterranean waters. Your knowledge of maps and charts is essential.

Conflict Resolution: Mediate disputes among the crew, helping to maintain a harmonious and productive environment.

Booty Distribution: When treasure is plundered, you'll help distribute the spoils fairly among the crew, keeping morale high.

Combat Readiness: Ensure that weapons and defenses are in top condition, ready for any skirmish or battle that may arise.

Qualifications:

Experience as a sailor or pirate in the 17th century Mediterranean.
Strong leadership and organizational skills.
Proficiency in navigation, map reading, and sailing.
Ability to make quick decisions under pressure.
Excellent interpersonal and conflict resolution skills.
Fearless spirit and a passion for adventure.

Benefits:

Adventure of a lifetime on the high seas.
Camaraderie with a diverse and passionate crew.
Opportunities for career advancement within the crew.
Competitive remuneration from shares of the plundered treasures, commensurate with experience and contribution to our pirate exploits.

How to Apply:

If you're ready to embrace the pirate's life and become our next Quartermaster, send your application via carrier pigeon (or a modern equivalent). Include your pirate name, a list of your past pirate adventures, and a brief message in a bottle telling us why you're the perfect fit for our crew.

Join Captain Blackbeard's Crew and make history on the Mediterranean waves! A pirate's life awaits you!
'''