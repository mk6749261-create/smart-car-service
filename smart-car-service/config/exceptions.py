class BusinessLogicError(Exception):
    """
    A validation/authorization failure raised by a business-logic (service)
    function. The message is safe to show directly to the end user (via the
    REST API or the AI Agent) - it never contains internal/technical detail.
    """
    pass

