@echo off
echo Przetwarzanie plików CSV...
python "%~dp0app.py" --input "%~dp0products_export.csv" --output "%~dp0filtered.csv" --cols "@id,/sizes/size@code_external,/sizes/size@code_producer,/parameters/parameter@textid[lang],/parameters/parameter@distinction,/parameters/parameter@group_distinction,/parameters/parameter@projector_hide,/prices_configuration_for_shops@value,/size_chart@id,/size_chart@name[lang],/group@id,/group/group_by_parameter@name[lang],/group/group_by_parameter/product_value@name[lang]" --langs "pol,lit,cze,hun,slo"
echo Przetwarzanie zakonczone. Wynik zapisano w plikach filtered.csv
pause
