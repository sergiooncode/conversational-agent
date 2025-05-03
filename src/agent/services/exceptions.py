class BaseServiceException(Exception):
    message = "A service raised an exception"


class OpenAIAgentNotConfiguredException(BaseServiceException):
    message = "OpenAI Agent not properly configured"


class OpenAIAgentRuntimeException(BaseServiceException):
    message = "OpenAI Agent threw an error while running"


class OpenAIAgentEmptyUserInputException(BaseServiceException):
    message = "OpenAI Agent received"
