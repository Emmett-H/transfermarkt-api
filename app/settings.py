from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env")
    RATE_LIMITING_ENABLE: bool = False
    RATE_LIMITING_FREQUENCY: str = "2/3seconds"
    API_KEY: str = "your-api-key-here"  # Default value, should be overridden in .env
    API_KEY_NAME: str = "x-api-key"     # Name of the header for the API key


settings = Settings()
