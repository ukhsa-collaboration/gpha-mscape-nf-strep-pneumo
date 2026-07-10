v0.2.0
Improved the should_run capability for integration into orchestration by adding
upstream context to the analysis record.

Added:
- Orange box version is parsed as a string in CLI. This is then incorporated into the analysis record.
- Onyx is queried for the versions and those (plus the automatically generated hash) are added
to the methods in the analysis record.

Changed:
- unit tests updated to check for the addition of the versions, including patching the query.
