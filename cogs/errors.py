from discord.ext import commands

class KekeException(commands.CommandError): 
    '''Common base class for bot exceptions'''

class InvalidRole(KekeException):
    '''A role was passed that wasn't specified in the bot settings'''
    def __init__(self, role, *args) -> None:
        self.role = role
        super().__init__(*args)

class EmptyInput(KekeException):
    '''No input passed'''

class BadHierarchy(KekeException):
    '''Role hierarchy is hecked'''

class MissingReactionRole(KekeException):
    '''The reaction role message is set but could not be found'''

class MissingFile(KekeException):
    '''Required file missing'''

class BadPrefix(KekeException):
    '''Bad prefix'''
    def __init__(self, prefix, *args) -> None:
        self.prefix = prefix
        super().__init__(*args)

class BadCommand(KekeException):
    '''Bad command'''
    def __init__(self, cmd, *args) -> None:
        self.cmd = cmd
        super().__init__(*args)

class BadFile(KekeException):
    '''Invalid file provided'''

class BadSettings(KekeException):
    '''Invalid settings provided'''
