from django import template
import logging

logger = logging.getLogger(__name__)
register = template.Library()

@register.filter
def get_item(dictionary, key):
    print(f"Key: {key}, Value: {dictionary.get(key)}")
    logger.debug(f"Dictionary: {dictionary}")
    logger.debug(f"Key: {key}, Value: {dictionary.get(key)}")
    return dictionary.get(key)

# @register.filter
# def get_item(dictionary, key):
#     for inner_dict in dictionary.values():
#         if key in inner_dict:
#             logger.info(f"Key: {key}, Value: {inner_dict.get(key)}")
#             return inner_dict.get(key)
#     logger.info(f"Key: {key} not found in dictionary")
#     return None
