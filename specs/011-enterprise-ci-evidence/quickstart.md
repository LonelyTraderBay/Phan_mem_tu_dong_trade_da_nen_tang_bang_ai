# Quickstart: CI tooling evidence

Local parity:

```powershell
cd BE_Bot_Auto_Trade_AI_Tu_Hoc\services\gateway
pip install -e ".[dev]"
python scripts\export_phase2_evidence.py
```

CI: `.github/workflows/phase2-tooling-evidence.yml`
