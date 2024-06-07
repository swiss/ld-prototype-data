# LD-Prototype-Data
Repo for dataschemes, testdata, and so on...

TODO: more information to come

Currently contains: 
- The [UPI dataset creation](UC-Serafe/UPI-Dataset-fiction) with the tarql script for the dataset of people's basic informations  
    Tarql was run on Windows
- The [EWR dataset creation](UC-Serafe/EWR-Dataset-fiction) with the tarql script for the dataset of people's principal residences  
    Tarql was run on Windows
- The [Python POC](UC-Serafe/client-POC) with SPARQL queries to two local SPARQL endpoints (EWR and UPI) that can be launched locally and easily  
    The POC was run on Ubuntu:
    - Launch the EWR endpoint with startEWR.sh  
    The endpoint is published on http://localhost:8000/  
    - Launch the UPI endpoint with startUPI.sh  
    The endpoint is published on http://localhost:8001/
    - Launch the client code with 3 parameters
    ```
    python3 serafe_sparql_query.py --queryNumber 5 --ewr_endpoint http://localhost:8000/ --upi_endpoint=http://localhost:8001/
    ```
    The parameter queryNumber to choose which query to run: 1-Federated SPARQL 2-Two queries 3-Multiple queries 4-Wikidata dereferencing 5-All
