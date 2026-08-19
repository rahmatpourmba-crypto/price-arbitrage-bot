from dataclasses import dataclass, field
from typing import Optional


@dataclass
class Supplier:
    name: str
    price: int
    site: str
    url: str
    shop_name: Optional[str] = None
    phone: Optional[str] = None
    location: Optional[str] = None
    seller_id: Optional[str] = None


@dataclass
class Buyer:
    title: str
    url: str
    site: str
    price: Optional[int] = None
    location: Optional[str] = None
    description: Optional[str] = None
    post_id: Optional[str] = None


@dataclass
class ArbitrageOpportunity:
    product_name: str
    supplier: Supplier
    buyer: Buyer
    profit: int = 0
    profit_margin: float = 0.0

    def __post_init__(self):
        if self.buyer.price and self.supplier.price:
            self.profit = self.buyer.price - self.supplier.price
            if self.supplier.price > 0:
                self.profit_margin = (self.profit / self.supplier.price) * 100


@dataclass
class SearchResult:
    suppliers: list[Supplier] = field(default_factory=list)
    buyers: list[Buyer] = field(default_factory=list)
    opportunities: list[ArbitrageOpportunity] = field(default_factory=list)
    errors: list[str] = field(default_factory=list)


def calculate_opportunities(suppliers: list[Supplier], buyers: list[Buyer]) -> list[ArbitrageOpportunity]:
    opps = []
    for sup in suppliers:
        for buy in buyers:
            if buy.price and sup.price and buy.price > sup.price:
                opp = ArbitrageOpportunity(
                    product_name=f"{sup.name}",
                    supplier=sup,
                    buyer=buy,
                )
                opps.append(opp)
    opps.sort(key=lambda o: o.profit, reverse=True)
    return opps
