v0.2.0
Improved the should_run capability for integration into orchestration by adding
upstream context to the analysis record from the samplesheet.

Added:
- Orange box version is parsed from the samplesheet in nextflow, then passed as a string into the
create_pneumokity_analysis_table.py. This is then incorporated into the analysis record.
- Teh script now queries Onyx for the versions and those (plus the automatically generated hash) are added
to the methods in the analysis record.

Changed:
- unit tests updated to check for the addition of the versions, including patching the query.
- Nextflow code (main.nf) now parses the 'context' (orange box version) from the samplesheet.
(This is now just a simple string. Previous commits had working versions where the samplesheet contained
valid yaml that would be parsed by the script that contained the onyx versions hash. )
