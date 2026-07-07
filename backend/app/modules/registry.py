"""Central import point for all module models.

Alembic autogenerate needs every model class imported so it is registered on
``Base.metadata``. As each module gains a ``models.py``, add one import line
here — nothing else should need to change when a new module is added.
"""


def import_all_models() -> None:
    from app.modules.audit import models as audit_models  # noqa: F401
    from app.modules.countries import models as countries_models  # noqa: F401
    from app.modules.auth import models as auth_models  # noqa: F401
    from app.modules.kyc import models as kyc_models  # noqa: F401
    from app.modules.ledger import models as ledger_models  # noqa: F401
    from app.modules.wallets import models as wallets_models  # noqa: F401
    from app.modules.topups import models as topups_models  # noqa: F401
    from app.modules.cards import models as cards_models  # noqa: F401
