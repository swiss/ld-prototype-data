# dedup: remove the duplicate triples, see https://github.com/tarql/tarql/issues/59
./tarql --delimiter semicolon --dedup 5000 mapping.sparql EWR_ResidencesPrincipales.csv > EWR_ResidencesPrincipales.ttl
