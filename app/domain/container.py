from dataclasses import dataclass
from app.domain.member import Member

@dataclass
class Container:
    member: Member
    image: str
    name: str = None   # member.id + label
    label: str = None
    running: bool = False
    
    