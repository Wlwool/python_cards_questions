import pytest
from pydantic import ValidationError

from app.config import Settings


class TestSettingsValidation:
    @pytest.mark.parametrize("field", ["admin_password", "secret_key"])
    def test_empty_secret_rejected(self, field):
        values = {"admin_password": "pw", "secret_key": "key"}
        values[field] = ""
        with pytest.raises(ValidationError):
            Settings(**values)
