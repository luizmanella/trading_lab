class NoModelError(Exception):
    def __init__(self):
        super().__init__("No strategy model was defined. Go back and define one.")

class SetUniverseFailure(Exception):
    def __init__(self):
        super().__init__("No security was set or no screening was done. Check your set_security_universe()")

class ClosingSecurityNotFound(Exception):
    def __init__(self, security):
        self.security = security
        self.message = f"Tried to close {security}, but position was not found."
        super().__init__(self.message)
    def __str__(self):
        return self.message

class BadModelName(Exception):
    def __init__(self):
        super().__init__("Duplicate model name. Please change one. If you don't have one use Test_Model.")


CUSTOM_EXCEPTIONS = {
    'no_model': NoModelError,
    'set_universe': SetUniverseFailure,
    'closing_security_issue': ClosingSecurityNotFound,
    'duplicate_model_name': BadModelName
}