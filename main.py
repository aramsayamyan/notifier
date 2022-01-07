import datetime
from pathlib import Path

from src.entities import Webinar, CompanyForWebinar, Company
from src.notifier import NotifyManager, load_notify_conditions


WEBINAR_NOTIFY_CONDITIONS = load_notify_conditions(
    conditions_file_path=Path(__file__).parent / 'notify_conditions.yaml',
    entity_type='Webinar'
)
COMPANY_FOR_WEBINAR_NOTIFY_CONDITIONS = load_notify_conditions(
    conditions_file_path=Path(__file__).parent / 'notify_conditions.yaml',
    entity_type='CompanyForWebinar'
)

created_webinar = Webinar(
    name='Webinar1',
    link='Webinar.com',
    start_date=datetime.datetime.now(),
)

notify_manager = NotifyManager(
    entity_type='Webinar',
    conditions=WEBINAR_NOTIFY_CONDITIONS,
    entity_obj=created_webinar
)

if notify_manager.should_be_notified():
    notify_manager.notify()
else:
    print("No need to notify the external API.")


company_for_webinar1 = CompanyForWebinar(
    company=Company(link='GetBrew.com', name='GetBrew', employees_min=1, employees_max=1000),
    webinar=created_webinar, is_blacklisted=True
)
company_for_webinar2 = CompanyForWebinar(
    company=Company(link='GetBrew.com', name='GetBrew', employees_min=1, employees_max=1000),
    webinar=created_webinar, is_blacklisted=False
)

notify_manager = NotifyManager(
    entity_type='CompanyForWebinar',
    conditions=COMPANY_FOR_WEBINAR_NOTIFY_CONDITIONS,
    entity_obj=company_for_webinar2,
    original_entity_obj=company_for_webinar1
)
if notify_manager.should_be_notified():
    notify_manager.notify()
else:
    print("No need to notify the external API.")
