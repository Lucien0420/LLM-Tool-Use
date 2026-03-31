"""Entry point: print loaded settings (use scripts/run_extract.py for extraction)."""

from app.core.config import get_settings


def main() -> None:
    s = get_settings()
    print("LLM_BASE_URL:", s.llm_base_url)
    print("LLM_MODEL:", s.llm_model)
    print("OPENAI_API_KEY set:", bool(s.openai_api_key))


if __name__ == "__main__":
    main()
