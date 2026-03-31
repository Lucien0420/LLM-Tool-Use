from unittest.mock import MagicMock, patch

from app.services.extract import InquiryExtractService, _parse_inquiry_json, _strip_json_fences
from app.schemas.inquiry import InquiryExtraction


def test_strip_json_fences():
    raw = '```json\n{"customer_name": "A", "contact": null, "estimated_budget": "1"}\n```'
    out = _strip_json_fences(raw)
    assert '"customer_name"' in out


def test_parse_inquiry_json():
    j = '{"customer_name": "Lee", "contact": "a@b.com", "estimated_budget": null}'
    m = _parse_inquiry_json(j)
    assert m.customer_name == "Lee"
    assert m.contact == "a@b.com"
    assert m.estimated_budget is None


def test_parse_inquiry_json_with_extra_text():
    raw = 'prefix {"customer_name": null, "contact": "09", "estimated_budget": "3k"} suffix'
    m = _parse_inquiry_json(raw)
    assert m.contact == "09"


@patch("app.services.extract.OpenAI")
def test_extract_from_text_calls_model(mock_openai_cls):
    mock_client = MagicMock()
    mock_openai_cls.return_value = mock_client
    mock_client.chat.completions.create.return_value = MagicMock(
        choices=[
            MagicMock(
                message=MagicMock(
                    content='{"customer_name":"John","contact":null,"estimated_budget":"~$200"}'
                )
            )
        ]
    )

    from app.core import config as cfg

    cfg.get_settings.cache_clear()
    try:
        svc = InquiryExtractService()
        r = svc.extract_from_text("sample inquiry body")
    finally:
        cfg.get_settings.cache_clear()

    assert r.customer_name == "John"
    assert r.estimated_budget == "~$200"
    mock_client.chat.completions.create.assert_called()


def test_extract_empty_returns_empty_model():
    from app.core import config as cfg

    cfg.get_settings.cache_clear()
    try:
        with patch("app.services.extract.OpenAI"):
            svc = InquiryExtractService()
            r = svc.extract_from_text("   \n  ")
    finally:
        cfg.get_settings.cache_clear()

    assert r == InquiryExtraction()
