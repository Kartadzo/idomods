@echo off
echo Przetwarzanie plików CSV...
python "%~dp0app.py" --input "%~dp0products_export.csv" --output "%~dp0filtered.csv" --cols "@id,/sizes/size@code_external,/sizes/size@code_producer,/delivery_time/mode@type,/delivery_time/time@days,/sum_in_basket@value,/associated_products/product@id,/hotspots/site@id,/hotspots/site@manual_config,/hotspots/site/promotion@visible,/hotspots/site/discount@visible,/hotspots/site/distinguished@visible,/hotspots/site/special@visible,/enable_in_pos@enabled,/availability_profile@id,/availability_management@value,/loyalty_program/site@id,/loyalty_program/site@operation,/loyalty_program/site@clients,/loyalty_program/site@points,/advance@rate,/priority@level,/sell_by/retail@quantity,/sell_by/wholesale@quantity,/inwrapper@quantity,/visibility/site@visible,/visibility/price_comparator@visible,/availability/site@id,/availability/site@value" --langs "pol,lit,cze,hun,slo"
echo Przetwarzanie zakonczone. Wynik zapisano w plikach filtered.csv
pause
