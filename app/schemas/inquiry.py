from pydantic import BaseModel, Field


class InquiryExtraction(BaseModel):
    """Structured fields aligned with LLM JSON output."""

    customer_name: str | None = Field(
        default=None,
        description="Customer name or how they introduce themselves",
    )
    contact: str | None = Field(
        default=None,
        description="Phone, email, or other contact (single string)",
    )
    estimated_budget: str | None = Field(
        default=None,
        description="Budget or price-related phrase as in the text",
    )

    model_config = {
        "json_schema_extra": {
            "examples": [
                {
                    "customer_name": "Jane Doe",
                    "contact": "+1-555-0100",
                    "estimated_budget": "around $5,000",
                }
            ]
        }
    }
