import reflex as rx

config = rx.Config(
    app_name="Paraprobar",
    #api_url="http://192.168.18.11:8000",  # Ej: "http://192.168.1.100:8000"
    upload_max_size=100_000_000,
    MAX_CONTENT_LENGTH = 100 * 1024 * 1024,  # 100MB
    #env=rx.Env.PROD  # Configurar entorno en producción
)