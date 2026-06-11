var Papa = require('papaparse');
var fs = require('fs');

var csvData = fs.readFileSync('images_concept_pro.csv', 'utf8'); // Wczytaj dane CSV z pliku

var parsedData = Papa.parse(csvData, {
    header: true,
    delimiter: ','
});

var aggregatedData = {};
parsedData.data.forEach(function(row) {
    var ean = row['EAN towaru'];
    if (!aggregatedData[ean]) {
        aggregatedData[ean] = row;
    } else {
        aggregatedData[ean]['Zdjęcie'] += ',' + row['Zdjęcie'];
    }
});

var csv = Papa.unparse(Object.values(aggregatedData));

fs.writeFile('ready.csv', csv, function(err) {
    if (err) {
        console.log('Wystąpił błąd podczas zapisywania pliku CSV: ' + err);
    } else {
        console.log('Plik CSV został pomyślnie zapisany.');
    }
});