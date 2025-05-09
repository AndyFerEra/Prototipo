import reflex as rx

config = rx.Config(
    app_name="Paraprobar",
    upload_max_size=100_000_000,
    MAX_CONTENT_LENGTH = 100 * 1024 * 1024,  # 100MB
)