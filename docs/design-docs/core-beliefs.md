# Core Beliefs

This repository is built around the following agent-first operating principles:

1. **Humans steer. Agents execute.** 
   There are ideally 0 lines of manually-written code in this repo. Even the scripts that test the agent are written by agents.
2. **No YOLO data probing.** 
   We validate data at the boundaries using strict typing (Pydantic/Typing) so the agent never has to "guess" shapes.
3. **Repository as Knowledge Base.** 
   Anything an agent cannot read in-repo (via `docs/` or code) does not exist. Slack messages and external design docs must be committed here. 
4. **Pedantic Mechanical Enforcement.** 
   We write custom linters for architectural rules, cross-linking, and consistency. We prefer automated "garbage collection" of AI slop over manual fixing.
5. **No 1000-page logic manuals.** 
   Avoid monolithic instruction files. Prefer progressive disclosure via table of contents and focused execution plans.
