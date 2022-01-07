import unittest


from .entities import Company
from .notifier import NotifyManager


class TestCompanyCreated(unittest.TestCase):

    def setUp(self) -> None:
        self.company1 = Company(
            link='https://www.getbrew.com/',
            name='GetBrew',
            employees_min=1,
            employees_max=1
        )

    def test_company_do_not_get_notified_when_it_is_not_newly_created(self):
        notify_manager = NotifyManager(
            entity_type='Company',
            entity_obj=self.company1,
            original_entity_obj=self.company1,
            conditions={
                'on_create': True
            }
        )
        self.assertEqual(notify_manager.should_be_notified(), False)

    def test_newly_created_company_should_be_notified_when_has_conditions(self):
        notify_manager = NotifyManager(
            entity_type='Company',
            entity_obj=self.company1,
            conditions={
                'on_create': True
            }
        )
        self.assertEqual(notify_manager.should_be_notified(), True)

    def test_newly_created_company_should_be_notified_when_has_do_not_have_condition(self):
        notify_manager = NotifyManager(
            entity_type='Company',
            entity_obj=self.company1,
            conditions={
                'on_create': False
            }
        )
        self.assertEqual(notify_manager.should_be_notified(), False)
