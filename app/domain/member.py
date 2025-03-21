from dataclasses import dataclass

@dataclass
class Member:
    id : int
    access_token : str
    refresh_token : str
    # name: str
    # age: int = 0  # 기본값 설정
    # email: str = "unknown@example.com"  # 기본값 설정