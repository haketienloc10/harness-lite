## Load Config

Before doing any role-specific work:

1. Read `_harness/config.yaml`.
2. Resolve:
   - `{user_name}`
   - `{communication_language}`
   - `{document_output_language}`

Language contract:
- User-facing communication must use `{communication_language}`.
- Artifact and document content must use `{document_output_language}`.