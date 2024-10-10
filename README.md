# LD-Prototype-Data
Currently contains: 
- The [UPI dataset creation](UC-Serafe/UPI-Dataset-fiction) based on a [tarql](https://tarql.github.io/) script for the dataset of people's basic informations  
    Tarql can be run on Windows or Linux with `run.bat` and `run.sh` respectively (found [here](UC-Serafe/UPI-Dataset-fiction/tarql-1.2/bin))  
- The [EWR dataset creation](UC-Serafe/EWR-Dataset-fiction) based on a [tarql](https://tarql.github.io/) script for the dataset of people's principal residences  
    Tarql can be run on Windows or Linux with `run.bat` and `run.sh` respectively (found [here](UC-Serafe/EWR-Dataset-fiction/tarql-1.2/bin))
- The [Python POC](UC-Serafe/client-POC) with SPARQL queries to two local SPARQL endpoints (EWR and UPI) that can be easily launched locally  
    The Python code relies on rdflib ([Code](https://github.com/RDFLib/rdflib) and [Documentation](https://rdflib.readthedocs.io/en/stable/))

    The POC was run on Ubuntu:
    - Launch the EWR endpoint with startEWR.sh  
    The endpoint is published on `http://localhost:8000/`
    - Launch the UPI endpoint with startUPI.sh  
    The endpoint is published on `http://localhost:8001/`
    - Run the client code with 3 parameters
        ```
        python3 serafe_sparql_query.py --queryNumber 5 --ewr_endpoint http://localhost:8000/ --upi_endpoint=http://localhost:8001/
        ```
        Use the parameter queryNumber to choose which query to run: 1-Federated SPARQL 2-Two queries 3-Multiple queries 4-Wikidata dereferencing 5-All

        To display the information about the expected parameters:
        ```
        python3 serafe_sparql_query.py
        ```

        **Remark**: The client code is sending SPARQL queries to the SPARQL end-points passed in parameters, this POC would thus work with any SPARQL end-point (and any triple store) that host the data

## About transforming XML to RDF
The exemples described here above are based on Tarql to transform CSV to RDF.  
The [XML2RDF](XML2RDF) folder contains example of tools to demonstrate how XML can be transformed to RDF:
- The [first example](XML2RDF/sparql-generate) is based on [sparql-generate](https://github.com/sparql-generate/sparql-generate)   
- The [second example](XML2RDF/rocketRML) is based on [rocketRML](https://github.com/semantifyit/RocketRML)  
See the documentation of the tool about its installation that might require [node.js and npm](https://docs.npmjs.com/downloading-and-installing-node-js-and-npm).

Both examples contain a `run.sh` to transform the file persons-eCH0044.xml. It is the same XML file in both examples, that contains 5 fictional caracters as a complement to the UPI dataset generated here above.  
More information will be given about those tools soon.


## Data validation - SHACL
RDF data can be validated with the [Shapes Constraint Language (SHACL)](https://www.w3.org/TR/shacl/).  
  
The generated UPI and EWR datasets, presented here above, are based and the SEMIC ontologies and can be validated with their provided SHACL files:  
- UPI dataset based on the [Core Person Vocabulary](https://semiceu.github.io/Core-Person-Vocabulary/releases/2.1.0/), find the SHACL file [here](https://semiceu.github.io/Core-Person-Vocabulary/releases/2.1.0/#shacl).  
- EWR dataset based on the [Core Criterion and Core Evidence Vocabulary](https://semiceu.github.io/CCCEV/releases/2.1.0/), find the SHACL file [here](https://semiceu.github.io/CCCEV/releases/2.1.0/#validation).  

To run the SHACL validation we use the [Apache Jena implementation](https://jena.apache.org/download/index.cgi) (Apache Jena Commands, version 5.1.0).  
  
The [shacl](shacl) folder contains the necessary tools and files to perform the SHACL validation:  
- The Jena tool unzipped in the `apache-jena-5.1.0` sub-folder   
- The two generated datasets  `UPI_Personnes_fiction.ttl` and `EWR_ResidencesPrincipales.ttl`  
- The SHACL files `core-person-ap-SHACL.ttl` and `cccev-ap-SHACL.ttl`  
Note: the `cccev-ap-SHACL.ttl` was adapted to `cccev-ap-SHACL_corrected.ttl` to avoid mixing http and https URLs for the time ontology
- `runUPI.sh` and `runEWR.sh` to execute the SHACL validation  

