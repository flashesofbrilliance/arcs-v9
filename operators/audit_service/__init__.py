# audit_service — Path A FastAPI audit layer
#
# Wires the operator pipeline (SAGE->LAB->BAR->KINTSUGI) behind
# four POST endpoints the compass route calls after inference.
#
# Run:
#     cd operators && uvicorn audit_service.main:app --port 8766
