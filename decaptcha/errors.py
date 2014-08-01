# -*- coding: utf-8 -*-

class SolverError(Exception):
    pass

class DecaptcherError(SolverError):
    pass

class RechargerError(Exception):
    pass

class CaptchaFound(RechargerError):
    pass
