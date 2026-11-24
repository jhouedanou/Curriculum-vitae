"""Point d'entrée du serveur pour l'application de bureau (Electron).

L'application choisit le port et le jeton, puis lance ce programme :
    JOBBOT_HOME=…  JOBBOT_PORT=…  JOBBOT_JETON=…  jobbot-serveur
Le serveur n'écoute que sur cet ordinateur (127.0.0.1).
"""
from __future__ import annotations

import os


def main() -> None:
    import uvicorn

    from .llm import charger_env
    from .web.serveur import app

    charger_env()
    port = int(os.environ.get("JOBBOT_PORT", "8765"))
    app.state.jeton = os.environ.get("JOBBOT_JETON") or "local"
    app.state.port = port
    app.state.local = True
    app.state.bureau = True
    uvicorn.run(app, host="127.0.0.1", port=port, log_level="warning")


if __name__ == "__main__":
    main()
