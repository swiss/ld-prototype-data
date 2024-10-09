const parser = require('rocketrml');

const doMapping = async () => {
  const options = {
    toRDF: true,
    verbose: true,
    xmlPerformanceMode: false,
    replace: false,
    removeNameSpace: {xmlns:"http://www.ech.ch/xmlns/eCH-0044/4"},
    functions: {
	      'http://example.com/grel.ttl#getSexUrl': function (data) {
		 if (data[0] == 1) {
		    return `http://publications.europa.eu/resource/authority/human-sex/MALE`;
		 } else {
		    return `http://publications.europa.eu/resource/authority/human-sex/FEMALE`;
		 }
              }
            },
  };
  const result = await parser.parseFile('./mapping.ttl', './result.n3', options).catch((err) => { console.log(err); });
  console.log(result);
};

doMapping();
