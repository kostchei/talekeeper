import pytest

from encounter_pane.campaign_frame import CampaignFrame
from services.campaign_description_service import CampaignDescriptionService


@pytest.fixture
def campaign_frame():
    data = {
        "name": "Test",
        "style": "grimdark",
        "monster_type_weights": {},
        "difficulty_distribution": {},
        "rest_rules": {},
        "available_classes": [],
    }
    return CampaignFrame(data)


def test_generate_description_fallback(campaign_frame):
    service = CampaignDescriptionService(base_url="http://127.0.0.1:9", request_timeout=0.1)
    description = service.generate_description(
        "monster",
        {"name": "Goblin Skirmisher", "type": "humanoid", "xp": 50},
        campaign_frame,
    )
    assert "Goblin Skirmisher" in description
    assert "grim" in description.lower()
