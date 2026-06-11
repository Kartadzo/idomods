var Papa = require('papaparse');
var fs = require('fs');

// Wczytaj dane CSV z plików
var csvData1 = fs.readFileSync('readyImagesBedConcept.csv', 'utf8');
var csvData2 = fs.readFileSync('attributtesBC.csv', 'utf8');

var parsedData1 = Papa.parse(csvData1, {
    header: true,
    delimiter: ','
});

var parsedData2 = Papa.parse(csvData2, {
    header: true,
    delimiter: ','
});

// Stwórz mapę danych z pierwszego pliku
var dataMap = {};
parsedData1.data.forEach(function(row) {
    dataMap[row['Kod towaru']] = row;
});

// Połącz dane z drugiego pliku
parsedData2.data.forEach(function(row) {
    var key = row['indeks bryły'];
    if (dataMap[key]) {
        // Połącz obiekty
        dataMap[key] = {...dataMap[key], ...row};
    }
});

var csv = Papa.unparse(Object.values(dataMap));

fs.writeFile('file_ready.csv', csv, function(err) {
    if (err) {
        console.log('Wystąpił błąd podczas zapisywania pliku CSV: ' + err);
    } else {
        console.log('Plik CSV został pomyślnie zapisany.');
    }
});