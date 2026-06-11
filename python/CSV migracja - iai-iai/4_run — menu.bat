@echo off
echo Przetwarzanie plików CSV...
python "%~dp0app.py" --input "%~dp0products_export.csv" --output "%~dp0filtered.csv" --cols "@id,/sizes/size@code_external,/sizes/size@code_producer,/navigation/site@id,/navigation/site/menu@id,/navigation/site/menu/item@textid[lang]" --langs "pol,lit,cze,hun,slo"
echo Przetwarzanie zakonczone. Wynik zapisano w plikach filtered.csv
pause
