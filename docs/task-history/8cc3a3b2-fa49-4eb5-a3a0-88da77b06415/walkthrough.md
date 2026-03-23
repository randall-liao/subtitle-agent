# Modernized Type Annotations in `google/genai/chats.py`

I have updated the `google/genai/chats.py` file to use modern PEP 604 pipe syntax (`X | Y`) for type annotations. This addresses the "Use `X | Y` for type annotations" problem, typically flagged by contemporary Python linters like Ruff.

## Changes Made

### Type Annotation Updates
- Replaced `Union[A, B]` with `A | B` across the file.
- Replaced `Optional[A]` with `A | None`.
- Added `from __future__ import annotations` to the top of the file for better compatibility and performance.
- Cleaned up `typing` imports by removing `Union` and `Optional`.

### File: [chats.py](file:///home/devuser/projects/subtitle-agent/.venv/lib/python3.14/site-packages/google/genai/chats.py)
The changes were applied to multiple methods, including:
- `_is_part_type`
- `Chat.send_message`
- `Chat.send_message_stream`
- `Chats.create`
- `AsyncChat.send_message`
- `AsyncChat.send_message_stream`
- `AsyncChats.create`

## Verification Results

### Syntax Check
I verified the changes using `py_compile`, which confirmed no syntax errors were introduced in the Python 3.14 environment.

```bash
python3.14 -m py_compile /home/devuser/projects/subtitle-agent/.venv/lib/python3.14/site-packages/google/genai/chats.py
```
> **Status**: DONE
> **Exit code**: 0
