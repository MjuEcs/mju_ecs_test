from dataclasses import dataclass

@dataclass
class Member:
    id : int
    access_token : str 
    refresh_token : str