def test_always_passes():
    assert True

def test_api_version():
    from apps.api.config import settings
    assert settings.PROJECT_NAME == "Hiqonis"
