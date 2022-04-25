from pydantic import BaseModel
from enum import Enum, auto
from typing import Dict, Optional

class Stage(Enum):
    GET_CURRENT_CURRENCY = auto()
    GET_NEW_TICKER = auto()
    GET_VALUE = auto()
    WAIT_FOR_COMMAND = ()

class Currency(BaseModel):
    ticker: Optional[str] = None
    sell: Optional[float] = None
    buy: Optional[float] = None


class User(BaseModel):
    currencies: Dict[str, Currency] = {}
    current_currency: Optional[Currency] = None
    selected: Optional[Currency] = None
    stage: Stage = Stage.GET_CURRENT_CURRENCY
