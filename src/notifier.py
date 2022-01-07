import yaml
from pathlib import Path
from typing import Optional, Callable

from .entities import ENTITY_TYPES
from .utils import notify_by_printing

# TODO: add logger


def load_notify_conditions(conditions_file_path: Path, entity_type: Optional[str] = None):
    """
    Read conditions yaml file from the specified path.
    Conditions yaml file will specify under which circumstances it is needed
    to notify the external service about the change of entity
    :param conditions_file_path: the path to the conditions yaml file
    :param entity_type: only return conditions for the requested entity_type, returns all if not specified
    :return: parsed yaml file
    """

    with open(conditions_file_path, 'r') as conditions_file_stream:
        all_conditions = yaml.safe_load(conditions_file_stream)

    if entity_type:
        return all_conditions[entity_type]
    return all_conditions


class NotifyManager:
    """
    This class will decide if it is needed to notify
     an external API based on the state of the entity.
    """

    def __init__(self, entity_type: str, conditions: dict, entity_obj=None, original_entity_obj=None):
        """
        Init the NotifyManager with the entity's old and new state
        :param entity_type: a string representing the entity type
        :param conditions: list of conditions to decide if it is needed to notify the external API
        :param entity_obj: An object representing an entity in its
         NEW/UPDATED state(might be None, if the object is now physically deleted)
        :param original_entity_obj: An object representing the same
         entity BEFORE the updated state
        (might be None, if this is an added entity)
        :raises TypeError: if entity_obj and original_entity_obj
         are of different types or if
        entity_type is not supported
        :raises ValueError: if neither entity_obj nor original_entity_obj is set
        :raises ValueError: if no conditions are present for the specified entity_type
        """

        if entity_type not in ENTITY_TYPES:
            raise TypeError(f"Unsupported type: {entity_type}")

        if entity_obj is None and original_entity_obj is None:
            raise ValueError("Either entity_obj or original_entity_obj should be set.")

        if (entity_obj and original_entity_obj) and type(entity_obj) != type(original_entity_obj):
            raise TypeError(
                "entity_obj and original_entity_obj should be of the same type."
            )

        # TODO: Maybe it's better to check if type of entity_obj
        #  and original_entity_obj matches entity_type.

        self.entity_obj = entity_obj
        self.original_entity_obj = original_entity_obj
        self.entity_type = entity_type
        self.conditions = conditions

    def should_be_notified(self) -> bool:
        """
        This functions decides if it is needed to notify about the changes of the obj
        The result is produced by checking the obj status against the dictionary of conditions
        """

        if not self.entity_obj and self.conditions.get('on_delete', False):
            # send delete notification only if it is explicitly set in the dictionary of conditions
            return True

        if not self.original_entity_obj and self.conditions.get('on_create', False):
            # send created notification only if it is explicitly set in the dictionary of conditions
            return True

        for changed_attribute, notifiable_change_values in self.conditions.get('on_change', {}).items():
            entity_obj_attr_value = getattr(self.entity_obj, changed_attribute, None)
            original_entity_obj_attr_value = getattr(self.original_entity_obj, changed_attribute, None)

            if entity_obj_attr_value != original_entity_obj_attr_value:
                # return True if the current value is the notifiable values otherwise False
                return entity_obj_attr_value in notifiable_change_values

        # no worthy change is detected or nothing has changed.
        return False

    @staticmethod
    def get_notifier(entity_obj) -> Callable:
        """
        Get appropriate notifier regarding the entity_obj
        :return: Callable that notifies the external API.
        """
        return notify_by_printing

    def notify(self):
        if self.conditions.get('notify_on_self', 'False'):
            self.get_notifier(self.entity_obj)(self.entity_obj)

        for notify_subject in self.conditions.get('notify_on_other', []):
            try:
                notify_subject_obj = getattr(self.entity_obj, notify_subject)
                self.get_notifier(notify_subject_obj)(notify_subject_obj)
            except AttributeError:
                # TODO: log the incident
                pass
