from app.schemas.inquiry import InquiryExtraction


def test_inquiry_extraction_optional_fields():
    data = InquiryExtraction(
        customer_name="Test",
        contact=None,
        estimated_budget="1–2k",
    )
    assert data.customer_name == "Test"
    assert data.contact is None


def test_inquiry_extraction_from_dict():
    d = {
        "customer_name": None,
        "contact": "test@example.com",
        "estimated_budget": None,
    }
    m = InquiryExtraction.model_validate(d)
    assert m.contact == "test@example.com"
