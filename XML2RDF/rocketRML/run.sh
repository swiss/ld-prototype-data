# rocketRML is installed according to the documentation of https://github.com/semantifyit/RocketRML
# run the transformation with 'node index.js'
node index.js
# Apply a correction to the resulting RDF in result.n3, to correct the sex string to a sex URL
sed -i 's#"http://publications.europa.eu/resource/authority/human-sex/MALE"#<http://publications.europa.eu/resource/authority/human-sex/MALE>#g; s#"http://publications.europa.eu/resource/authority/human-sex/FEMALE"#<http://publications.europa.eu/resource/authority/human-sex/FEMALE>#g' result.n3
