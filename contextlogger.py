import logging
from logging import LoggerAdapter, Logger
from typing import Union


class ContextLogger(LoggerAdapter):
  """
  Implementation of a nestable LoggerAdapter, because the one in the standard library does not merge extra metadata
  """

  def __init__(self,
               logger: Union[Logger, LoggerAdapter, 'ContextLogger'],
               context: dict):
    # LoggerAdapter uses 'extra' variable correctly only if using Logger
    #  instance as 'logger' variable and not another LoggerAdapter instance.
    self.logger = logger.logger if hasattr(logger, 'logger') else logger
    self.context = {**logger.context, **context} if hasattr(logger, 'context') else context
    super().__init__(self.logger, dict(context=self.context))


if __name__ == '__main__':
  """
  Documentation by a basic usage example / Manual unit test 
  
  >>> Output:
  {
    "message": "Message 1"
  }
  {
      "message": "Message 2",
      "context": {
          "foo": "original",
          "bar": "original"
      }
  }
  {
      "message": "Message 3",
      "context": {
          "foo": "updated",
          "bar": "original",
          "new": 123
      }
  }
  """
  import json


  class BasicContextAppender(logging.Filter):
    def filter(self, record):
      msg_data = {
        'message': record.msg,
      }
      if hasattr(record, 'context'):
        msg_data['context'] = record.context
      record.msg = json.dumps(msg_data, indent=4)
      return True  # True means that this logging event is recorded


  logger = logging.getLogger()
  logger.setLevel(logging.INFO)
  stream_handler = logging.StreamHandler()
  stream_handler.addFilter(BasicContextAppender())
  logger.addHandler(stream_handler)

  logger.info('Message 1')

  context2 = {
    'foo': 'original',
    'bar': 'original'
  }
  logger2 = ContextLogger(logger, context2)
  logger2.info('Message 2')

  context3 = {
    'foo': 'updated',
    'new': 123
  }
  logger3 = ContextLogger(logger2, context3)
  logger3.info('Message 3')
