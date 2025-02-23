from enum import Enum

class UserRole(str, Enum):
    admin = "Admin"
    doctor = "Doctor"
    radiologist = "Radiologist"

class Gender(str, Enum):
    male = "Male"
    female = "Female"

class TreatmentStatus(str, Enum):
    ongoing = "Ongoing"
    completed = "Completed"

class SeverityLevel(int, Enum):
    mild = 1
    moderate = 2
    severe = 3
    critical = 4
