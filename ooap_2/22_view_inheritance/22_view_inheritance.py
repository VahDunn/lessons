# Вариант с множеством классов

class Employee:
    pass


class Programmer(Employee):
    pass


class Engineer(Employee):
    pass


class Manager(Employee):
    pass


class Permanent(Employee):
    pass


class Contractor(Employee):
    pass


class PermanentProgrammer(Programmer, Permanent):
    pass


class ContractProgrammer(Programmer, Contractor):
    pass


class PermanentEngineer(Engineer, Permanent):
    pass


class ContractManager(Manager, Contractor):
    pass


# и т.д.

# Вариант с композицией/встраиванием

class Contract:
    pass


class PermanentContract(Contract):
    pass


class ContractorContract(Contract):
    pass


class EmployeeWithContract:
    def __init__(self, contract: Contract):
        self.contract = contract


class ProgrammerWithContract(EmployeeWithContract):
    pass


class EngineerWithContract(EmployeeWithContract):
    pass


class ManagerWithContract(EmployeeWithContract):
    pass


programmer1 = ProgrammerWithContract(PermanentContract())
programmer2 = ProgrammerWithContract(ContractorContract())
engineer = EngineerWithContract(PermanentContract())
manager = ManagerWithContract(ContractorContract())


# и т.д.