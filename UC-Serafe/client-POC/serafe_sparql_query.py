"""
Prototyp Linked master Data - BK
Serafe use-case
Author: Fabian Cretton - HES-SO Valais/Wallis - Institut Informatique Sierre

Testing a few ways to run SPARQL queries over different SPARQL endpoints

Code based on Python's RDFLib that must be installed
    Code: https://github.com/RDFLib/rdflib
    Documentation: https://rdflib.readthedocs.io/en/stable/

To run this code, two SPARQL endpoints must be up and running:
    - EWR endpoint
    - UPI endpoint
    This folder contains little datasets as .ttl files, one for EWR and one for UPI
    Those .ttl files can be uploaded in a SPARQL endpoint, see the startEWR.sh and startUPI.sh scripts

Then script is started with 3 command line parameters: the queries to run and the endpoints URLs:
    --queryNumber=5 --ewr_endpoint=http://localhost:8000/, --upi_endpoint=http://localhost:8001/

    queryNumber possible values: 1-Federated 2-Two queries 3-Multiple queries 4-Wikidata dereferencing 5-All queries
"""

import logging
import sys, os
import argparse
from pathlib import Path
import time
import rdflib
from SPARQLWrapper import SPARQLWrapper, JSON
import requests
from http.client import HTTPConnection

def queryLocalFile():
    """
    A basic example to run a SPARQL query over a file content, without triple store
    """

    g = rdflib.Graph()
    g.parse(f"UPI_Personnes_fiction.ttl", format="turtle")

    for row in g.query("SELECT ?s WHERE { ?s ?p ?o .}"):
        # For select queries, the Result object is an iterable of ResultRow
        # objects.
        assert isinstance(row, rdflib.query.ResultRow)
        print(row.s)
        # or row["s"]
        # or row[rdflib.Variable("s")]

def queryEndPointsOneFederatedQuery(EWREndpoint, UPIEndpoint) :
    """
    Perform a single SPARQL federated query over the EWR and UPI endpoints
    Querying people with a principal residence on the EWR
    and then people name and surname at the UPI
    """

    queryString = """
        PREFIX dct:  <http://purl.org/dc/terms/>
        PREFIX foaf:  <http://xmlns.com/foaf/0.1/>
        PREFIX ex: <http://example.com/>
        PREFIX cv:  <http://data.europa.eu/m8g/> 
        PREFIX locn: <http://www.w3.org/ns/locn#> 
        SELECT ?evidence ?person ?postCode ?city ?name ?surname WHERE {
        ?evidence dct:conformsTo ex:evidenceTypeEWRMeldeverhaeltnisPrincipalResidence ;
          dct:subject ?person ;
          cv:registeredAddress ?adr .
        ?adr locn:postCode ?postCode ;
          locn:postName ?city .

        SERVICE <""" + UPIEndpoint + """> {
            ?person foaf:familyName ?name .
            OPTIONAL{?person foaf:givenName ?surname}
            }
        } order by ?name ?surname
        """
    
    sparql = SPARQLWrapper(EWREndpoint)

    print("FEDERATED QUERY")
    print("===============")

    sparql.setQuery(queryString)

    try:
        sparql.setReturnFormat(JSON)
        results = sparql.query().convert()

        print("Query results: "  + str(len(results["results"]["bindings"])))

        for result in results["results"]["bindings"]:
            # handle OPTIONAL 'surname' value
            if "surname" in result:
                print(result["name"]["value"] + " " + result["surname"]["value"] + " (" + result["postCode"]["value"] + " " + result["city"]["value"] + ")")
            else:
                print(result["name"]["value"] + " [no available surname] (" + result["postCode"]["value"] + " " + result["city"]["value"] + ")")

    # ret is a stream with the results in XML, see <http://www.w3.org/TR/rdf-sparql-XMLres/>
    except Exception as err:
        print(f"Unexpected {err=}, {type(err)=}")

def queryEndPointsTwoQueries(EWREndpoint, UPIEndpoint) :
    """
    Replace the federated query by two queries:
        Perform a first SPARQL query at the EWR endpoint, and then another query at the UPI endpoints

    Instead of the joints feasible with a federated query, the results of the first query are used for the VALUE restriction of the variable values in the second query

    Querying people with a principal residence on the EWR
    and then people name and surname at the UPI
    """
    
    queryStringEWR = """
        PREFIX dct:  <http://purl.org/dc/terms/>
        PREFIX ex: <http://example.com/>
        PREFIX cv:  <http://data.europa.eu/m8g/> 
        PREFIX locn: <http://www.w3.org/ns/locn#> 
        SELECT ?evidence ?person ?postCode ?city WHERE {
        ?evidence dct:conformsTo ex:evidenceTypeEWRMeldeverhaeltnisPrincipalResidence ;
          dct:subject ?person ;
          cv:registeredAddress ?adr .
        ?adr locn:postCode ?postCode ;
          locn:postName ?city .
        } """

    queryStringUPI = """
        PREFIX foaf:  <http://xmlns.com/foaf/0.1/>
        SELECT ?person ?name ?surname WHERE {
        VALUES ?person { PERSON_VALUES_TO_REPLACE }
  	    ?person foaf:familyName ?name .
	    OPTIONAL{?person foaf:givenName ?surname}	
        } order by ?name ?surname
        """

    print("\nTWO QUERIES")
    print("===========")
    
    sparqlEWR = SPARQLWrapper(EWREndpoint)
    sparqlUPI = SPARQLWrapper(UPIEndpoint)

    sparqlEWR.setQuery(queryStringEWR)

    personValues = ""

    try:
        sparqlEWR.setReturnFormat(JSON)
        results = sparqlEWR.query().convert()

        print("EWR query results: "  + str(len(results["results"]["bindings"])))

        arrayAddresses = {}

        for result in results["results"]["bindings"]:
            personValues += "<" + result["person"]["value"] + "> "
            arrayAddresses[result["person"]["value"]] = result["postCode"]["value"] + " " + result["city"]["value"]

        print("\nPerson list for VALUE in the UPI query: " + personValues )
        queryStringUPI = queryStringUPI.replace("PERSON_VALUES_TO_REPLACE", personValues)   
        #print("UPI final query: " + queryStringUPI)

        sparqlUPI.setQuery(queryStringUPI)
        sparqlUPI.setReturnFormat(JSON)
        results = sparqlUPI.query().convert()

        print("\nUPI query results: " + str(len(results["results"]["bindings"])))
        for result in results["results"]["bindings"]:
            person = result["person"]["value"]

            # handle OPTIONAL 'surname' value
            if "surname" in result:
                surnameValue = result["surname"]["value"] 
            else:
                surnameValue = "[no available surname]"


            if person in arrayAddresses:
                print(result["name"]["value"] + " " + surnameValue + " (" +  arrayAddresses[person] + ")")
            else:
                print(result["name"]["value"] + " " + surnameValue + " (No available address)")

    # ret is a stream with the results in XML, see <http://www.w3.org/TR/rdf-sparql-XMLres/>
    except Exception as err:
        print(f"Unexpected {err=}, {type(err)=}")

def queryEndPointsOneQueryPerPerson(EWREndpoint, UPIEndpoint) :
    """
    Perform a first SPARQL query at the EWR endpoint, and then one query 
    Then the loop on the first query result performs one query for each person at the UPI endpoint
        Note: in queryEndPointsTwoQueries() the loop is used to create the list of persons identifier 
            to be used in the VALUES clause of a single second query to the UPI endpoint.
    """    
    queryStringEWR = """
        PREFIX dct:  <http://purl.org/dc/terms/>
        PREFIX ex: <http://example.com/>
        PREFIX cv:  <http://data.europa.eu/m8g/> 
        PREFIX locn: <http://www.w3.org/ns/locn#> 
        SELECT ?evidence ?person ?postCode ?city WHERE {
        ?evidence dct:conformsTo ex:evidenceTypeEWRMeldeverhaeltnisPrincipalResidence ;
            dct:subject ?person ;
            cv:registeredAddress ?adr .
        ?adr locn:postCode ?postCode ;
            locn:postName ?city .
        } """

    queryStringUPI = """
        PREFIX foaf:  <http://xmlns.com/foaf/0.1/>
        SELECT ?name ?surname WHERE {
        PERSON_URI_TO_REPLACE foaf:familyName ?name .
	    OPTIONAL{PERSON_URI_TO_REPLACE foaf:givenName ?surname}	
        }    
        """

    print("\nMULTIPLE QUERIES")
    print("===========")
    
    sparqlEWR = SPARQLWrapper(EWREndpoint)
    sparqlUPI = SPARQLWrapper(UPIEndpoint)

    sparqlEWR.setQuery(queryStringEWR)

    try:
        sparqlEWR.setReturnFormat(JSON)
        results = sparqlEWR.query().convert()

        print("EWR query results: "  + str(len(results["results"]["bindings"])))

        for result in results["results"]["bindings"]:
            print("UPI query for " + result["person"]["value"])
            personURL = "<" + result["person"]["value"] + ">"
            queryStringUPIFinal = queryStringUPI.replace("PERSON_URI_TO_REPLACE", personURL)   
            sparqlUPI.setQuery(queryStringUPIFinal)
            sparqlUPI.setReturnFormat(JSON)
            resultsUPI = sparqlUPI.query().convert()
            #print("UPI query results: "  + str(len(resultsUPI["results"]["bindings"])))
            for resultUPI in resultsUPI["results"]["bindings"]:
                # handle OPTIONAL 'surname' value
                if "surname" in resultUPI:
                    surnameValue = resultUPI["surname"]["value"] 
                else:
                    surnameValue = "[no available surname]"
                    
                print(resultUPI["name"]["value"] + " " + surnameValue + " (" + result["postCode"]["value"] + " " + result["city"]["value"] + ")")

    # ret is a stream with the results in XML, see <http://www.w3.org/TR/rdf-sparql-XMLres/>
    except Exception as err:
        print(f"Unexpected {err=}, {type(err)=}")

def queryWikidataDereferencing(UPIEndpoint) :
    """
    This test is different than the others.
    Perform a first query to the UPI end-point to get all the Wikidata URLs of the people
    Then the loop on the first query result performs an HTTP Get of the person's URL to Wikidata
        Here there is no way to query specific values for that ressource (only name/surname for instance), the full document will be retrieved
    """      
    #url = 'http://www.wikidata.org/entity/Q111082709'
    headers = {'Accept': 'application/json'}

    queryStringUPI = """
        PREFIX rdfs:  <http://www.w3.org/2000/01/rdf-schema#>
        SELECT ?wikiUrl WHERE {
        ?person rdfs:seeAlso ?wikiUrl .
        }  LIMIT 8  
        """

    print("\nWIKIDATA DEREFERENCING (max 8 results)")
    print("========================================")
    
    sparqlUPI = SPARQLWrapper(UPIEndpoint)

    sparqlUPI.setQuery(queryStringUPI)

    try:
        sparqlUPI.setReturnFormat(JSON)
        results = sparqlUPI.query().convert()

        print("UPI query results of wikidata URLs: "  + str(len(results["results"]["bindings"])))

        for result in results["results"]["bindings"]:
            wikidataURL = result["wikiUrl"]["value"]
            print("HTTP GET " + wikidataURL)
            resp = requests.get(wikidataURL, headers=headers)
            #results = resp.json()
            #print("Get result:")
            #print(resp)
            # for entity in results["entities"]:
            #     print(entity)
            # This is not yet the label, to be further analyzed if needed
            #     for labelValue in results["entities"][entity]["labels"]["en"] :
            #         print(labelValue["value"])

    except Exception as err:
        print(f"Unexpected {err=}, {type(err)=}")

if __name__ == "__main__":
    # NOTE: this debug level will also be used for the HTTP Get requests
    logging.basicConfig(level=logging.ERROR, stream=sys.stderr)

    # read command line arguments
    parser=argparse.ArgumentParser()

    parser.add_argument("--queryNumber", help="A number for the query/ies to execute: 1-Federated 2-Two queries 3-Multiple queries 4-Wikidata dereferencing 5-All queries")
    parser.add_argument("--ewr_endpoint", help="The SPARQL endpoint URL for EWR")
    parser.add_argument("--upi_endpoint", help="The SPARQL endpoint URL for UPI")

    args=parser.parse_args()

    if args.ewr_endpoint == None or args.upi_endpoint == None:
        print("Please launch the programm with the needed command line arguments")
        print(parser.format_help())
        os._exit(1)

    print("\nProgram started with following parameters:")
    print(args) 
    print()
    
    # Not used currently:
    # A basic example to run a SPARQL query over a file content, without triple store
    # queryLocalFile()

    executionDurations = ""

    # Run a specific query (1 to 4) or all queries (5)
    if args.queryNumber == "1" or args.queryNumber == "5":
        start_time = time.time()
        queryEndPointsOneFederatedQuery(args.ewr_endpoint, args.upi_endpoint)
        federatedQueryDuration = round(time.time() - start_time, 2)
        executionDurations += "One federated query:                                         " + str(round(time.time() - start_time, 2)) + "\n"

    if args.queryNumber == "2" or args.queryNumber == "5":
        start_time = time.time()
        queryEndPointsTwoQueries(args.ewr_endpoint, args.upi_endpoint)
        twoQueriesDuration = round(time.time() - start_time, 2)
        executionDurations += "One query to EWR and one query to UPI                        " + str(round(time.time() - start_time, 2)) + "\n"

    if args.queryNumber == "3" or args.queryNumber == "5":
        start_time = time.time()
        queryEndPointsOneQueryPerPerson(args.ewr_endpoint, args.upi_endpoint)
        multipleQueriesDuration = round(time.time() - start_time, 2)
        executionDurations += "One query to EWR and One query per person to UPI             " + str(round(time.time() - start_time, 2)) + "\n"

    if args.queryNumber == "4" or args.queryNumber == "5":
        start_time = time.time()
        queryWikidataDereferencing(args.upi_endpoint) 
        wikidataDereferencingDuration = round(time.time() - start_time, 2)
        executionDurations += "One query to EWR and one http request per person to Wikidata " + str(round(time.time() - start_time, 2)) + "\n"

    # Print the execution durations at the end of the script
    print("\nExecution durations:")
    print("=====================")
    print(executionDurations)
    print("IMPORTANT: those durations are only informative.\nMoreover, the very first query sent to a triple store can induce a triple store warm-up.\nTherefore, just after the launch of the triple store, please run the test twice to avoid a longer execution time for the first query.")