"""
# Definición del logger root
# -----------------------------------------------------------------------------
# ======================= MAIN SCRIPT ============================================
"""
import logging
logging.basicConfig( level=logging.INFO )
""" 
from pythonjsonlogger import jsonlogger
logHandler = logging.FileHandler('GraphQL.log')
logHandler.setLevel(logging.DEBUG)
class CustomDebugnFormatter(jsonlogger.JsonFormatter):
    def add_fields(self, log_record, record, message_dict):
        server = 'GraphQL-DB'
        super(CustomDebugnFormatter, self).add_fields(
            log_record, record, message_dict)
        if log_record.get('level'):
            log_record['level'] = log_record['level'].upper()
        else:
            log_record['level'] = record.levelname
            log_record['server'] = server
formatter = CustomDebugnFormatter(
    '%(server)s %(asctime)s %(level)s %(name)s %(message)s')
logHandler.setFormatter(formatter)
logging.getLogger('').addHandler(logHandler)
consola_handler = logging.StreamHandler()
consola_handler.setLevel(logging.INFO)
class CustomJsonFormatter(jsonlogger.JsonFormatter):
    def add_fields(self, log_record, record, message_dict):
        server = 'GraphQL-DB'
        super(CustomJsonFormatter, self).add_fields(
            log_record, record, message_dict)
        if log_record.get('level'):
            log_record['level'] = log_record['level'].upper()
        else:
            log_record['level'] = record.levelname
            log_record['server'] = server
consola_handler_formatter = CustomJsonFormatter(
    '%(server)s %(asctime)s %(level)s %(name)s %(message)s')
consola_handler.setFormatter(consola_handler_formatter)
#logging.getLogger('').addHandler(consola_handler)
"""