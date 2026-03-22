# Spec: New User Onboarding

## The Problem
Python CLI tools are notoriously difficult to distribute to non-developers. "Virtual environments", "pip installs", and "PATH variables" are blockers.

## The Spec
Subtitle Agent onboarding MUST adhere to the following simple funnel:

1. **Prerequisite Triviality**: 
   - We enforce the usage of `uv` because it requires no pre-existing Python environment management. 
   - A simple `curl` or `powershell` one-liner is the only requirement for the user.

2. **No Compilation / Git requirements**:
   - The user must be instructed to download the repository `.zip` directly from GitHub. `git clone` remains an optional advanced track.

3. **Flat Configs**:
   - Environment variables are managed solely through a root `.env` file containing the 3 absolute required keys (Gemini, TMDB, SubDL).

Any new feature proposals that compromise this 3-step installation must be mechanically rejected.
