# Note: a modification/correction was done in the original SHACL file from SEMIC
# because it was mixing http and https URLs for the time ontology
# The corrected file uses http URLs
apache-jena-5.1.0/bin/shacl validate --shapes cccev-ap-SHACL_corrected.ttl --data EWR_ResidencesPrincipales.ttl

