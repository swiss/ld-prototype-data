# First prepare the .xml file for the current version of sparql-generate that can not handle XML tags that contain camelCase
# Therefore create a new file where all the tags are lowercase
sed -r 's/<\/?[^>]+/\L&/g' persons-eCH0044.xml > persons-eCH0044_noCapitals.xml
# Then create a copy of query.rqg in which the source file will be defined
# As the sourcefile does include the path, it must be updated with the current working folder
cp query.rqg queryUpdated.rqg
sed -i 's#<SOURCE_FILE>#'"<file:///$(pwd)/persons-eCH0044_noCapitals.xml>"'#g' queryUpdated.rqg
# Then run the transformation to RDF and save the result in 'result.ttl'
java -jar sparql-generate-2.1.0.jar -q queryUpdated.rqg -o result.ttl
