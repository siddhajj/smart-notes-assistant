import pynecone as pc

config = pc.Config(
    app_name="web",
    db_url="sqlite:///pynecone.db",
    env="dev",
)
