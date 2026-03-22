# Frontend Application

Subtitle Agent is a **headless CLI tool**. It inherently does not possess a graphical user interface (GUI) or browser-facing frontend.

## CLI Aesthetics
We aim for clear, colorful, and engaging terminal output rather than raw text dumps.
- **Loguru** is utilized globally (`src/main.py`) to provide vibrant, severity-colored logging.
- Agent actions trace their internal thoughts using standard LLM verbose output routing when in debug modes.
- End-user interfaces are restricted to `argparse` configurations.

If a GUI is ever implemented, it should be a standalone Desktop wrapper (Electron/Tauri) invoking the Python CLI binary natively.
