@echo off
echo Przetwarzanie plików CSV...
python "%~dp0app.py" --input "%~dp0products_export.csv" --output "%~dp0filtered.csv" --cols "@id,/sizes/size@id,/sizes/size@name,/sizes/size@code_producer,/sizes/size@code_external" --langs "pol,lit,cze,hun,slo"
echo Przetwarzanie zakonczone. Wynik zapisano w plikach filtered.csv
pause
