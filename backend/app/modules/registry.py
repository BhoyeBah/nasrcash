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
    from app.modules.withdrawals import models as withdrawals_models  # noqa: F401
    from app.modules.cards import models as cards_models  # noqa: F401
    from app.modules.fx import models as fx_models  # noqa: F401
    from app.modules.payments import models as payments_models  # noqa: F401
    from app.modules.notifications import models as notifications_models  # noqa: F401
    from app.modules.admin import models as admin_models  # noqa: F401
    from app.modules.limits import models as limits_models  # noqa: F401
