# Frozen fixture root (self-test only)

`jtbd_graph_schema_check.py --self-test` runs the KEY-LOOKUP fixtures against this folder,
not the live repo, so regenerating the real catalogs never breaks the self-test.
Files are copies from commit b59b255f (when the fixtures were authored); the long ones are
cut after the last cited line, so they are line-addressed text, not valid JSON. Do not regenerate.
The real graph still checks against the live repo (`--check`).
