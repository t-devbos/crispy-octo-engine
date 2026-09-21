"""Antwoord — KERN 05.1.

**Waarom we een float weigeren in ``__init__``.** De hele class bestaat zodat
geld geen float kan zijn. Hem accepteren en omrekenen zou het precisieverlies
stil binnenlaten: ``Money(2.675 * 100)`` is ``Money(267)`` en niet
``Money(268)``, omdat 2,675 niet exact weer te geven is.

Weigeren aan de grens is de hele waarde van een waardeobject: het is één plek
waar ongeldige toestanden worden tegengehouden, in plaats van overal
gecontroleerd.

**``NotImplemented``, niet ``False``.** ``False`` teruggeven uit ``__eq__`` zegt
"deze zijn beslist verschillend". ``NotImplemented`` teruggeven zegt "ik weet
niet hoe ik deze moet vergelijken". Python probeert dan ``other.__eq__(self)``,
en valt pas terug op ``False`` als die het ook niet weet.

**``__hash__`` is niet optioneel.** ``__eq__`` definiëren zet ``__hash__`` op
``None``, en het object wordt onbruikbaar in een set of als dict-key — met een
foutmelding die ``__eq__`` nergens noemt. Dat was vraag h. De regel: gelijke
objecten moeten gelijke hashes hebben, dus hash precies de velden die ``__eq__``
vergelijkt.

**``from_euros`` neemt een string.** Zodra je een float hebt, is de precisie al
weg. Een classmethod die ``"249.00"`` parst, is het laatste punt waarop de
waarde nog exact is. Let erop dat hij ``"0.5"`` net zo goed aankan als
``"0.50"`` — een breukdeel van één cijfer komt echt voor in handgemaakte CSV's.
"""

from __future__ import annotations

class Money:
    """Een geldbedrag in hele centen."""

    def __init__(self, cents: int, currency: str = "EUR"):
        if isinstance(cents, bool) or not isinstance(cents, int):
            # bool is een subclass van int, en Money(True) is nooit de bedoeling.
            raise TypeError(f"cents moet een int zijn, kreeg {type(cents).__name__}")
        self.cents = cents
        self.currency = currency

    # --- weergave ----------------------------------------------------------
    def __repr__(self) -> str:
        return f"Money({self.cents}, {self.currency!r})"

    def __str__(self) -> str:
        return f"{self.currency} {self.cents / 100:,.2f}"

    # --- gelijkheid --------------------------------------------------------
    def __eq__(self, other) -> bool:
        if not isinstance(other, Money):
            return NotImplemented
        return (self.cents, self.currency) == (other.cents, other.currency)

    def __hash__(self) -> int:
        return hash((self.cents, self.currency))

    # --- rekenen -----------------------------------------------------------
    def __add__(self, other: Money) -> Money:
        self._same_currency(other)
        return Money(self.cents + other.cents, self.currency)

    def __sub__(self, other: Money) -> Money:
        self._same_currency(other)
        return Money(self.cents - other.cents, self.currency)

    def __mul__(self, factor: int) -> Money:
        if isinstance(factor, bool) or not isinstance(factor, int):
            raise TypeError(
                "Money kan alleen met een int vermenigvuldigd worden - een float "
                "vraagt om een afrondingsregel die de aanroeper moet kiezen"
            )
        return Money(self.cents * factor, self.currency)

    __rmul__ = __mul__          # zodat 3 * Money(100) ook werkt

    # --- sorteren ----------------------------------------------------------
    def __lt__(self, other: Money) -> bool:
        self._same_currency(other)
        return self.cents < other.cents

    def __le__(self, other: Money) -> bool:
        self._same_currency(other)
        return self.cents <= other.cents

    # --- intern ------------------------------------------------------------
    def _same_currency(self, other: Money) -> None:
        if self.currency != other.currency:
            raise ValueError(f"verschillende valuta: {self.currency} en {other.currency}")

    # --- aanmaken ----------------------------------------------------------
    @classmethod
    def from_euros(cls, amount: str, currency: str = "EUR") -> Money:
        """Parse een decimale string als ``"249.00"`` naar centen.

        Neemt expres een string en geen float: een float is de precisie die deze
        class beschermt al kwijt.
        """
        whole, _, fraction = amount.strip().partition(".")
        fraction = (fraction + "00")[:2]        # "5" -> "50", "" -> "00"
        return cls(int(whole) * 100 + int(fraction), currency)


if __name__ == "__main__":
    price = Money(24900)
    assert price.cents == 24900
    assert price.currency == "EUR"
    try:
        Money(249.0)
    except TypeError:
        pass
    else:
        raise AssertionError("een bedrag als float hoort geweigerd te worden")

    assert repr(Money(24900)) == "Money(24900, 'EUR')"
    assert str(Money(24900)) == "EUR 249.00"
    assert str(Money(1234567)) == "EUR 12,345.67"

    assert Money(100) == Money(100)
    assert Money(100) != Money(100, "USD")
    assert Money(100) != 100
    assert len({Money(100), Money(100), Money(200)}) == 2

    assert Money(24900) + Money(11950) == Money(36850)
    assert Money(24900) - Money(900) == Money(24000)
    assert Money(24900) * 3 == Money(74700)
    assert 3 * Money(24900) == Money(74700)
    try:
        Money(100, "EUR") + Money(100, "USD")
    except ValueError:
        pass
    else:
        raise AssertionError("valuta mengen hoort een error te geven")

    assert Money(100) < Money(200)
    assert sorted([Money(300), Money(100), Money(200)]) == [
        Money(100), Money(200), Money(300),
    ]

    assert Money.from_euros("249.00") == Money(24900)
    assert Money.from_euros("0.05") == Money(5)
    assert Money.from_euros("0.5") == Money(50)
    assert Money.from_euros("1234.56", "USD") == Money(123456, "USD")

    print("alles correct")
