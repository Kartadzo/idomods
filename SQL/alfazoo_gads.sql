SELECT
    customer.id_customer as 'ID',
    customer.firstname as 'First Name',
    customer.lastname as 'Last Name',
    country.iso_code as Country,
    address.postcode as Zip,
    address.phone as Phone,
    customer.email as Email
FROM
    ps_customer customer
    LEFT JOIN ps_address address ON address.id_customer = customer.id_customer
    LEFT JOIN ps_country country ON country.id_country = address.id_country
    LEFT JOIN ps_orders o ON o.id_customer = customer.id_customer
WHERE
    (customer.deleted = 0)
    AND (customer.id_shop IN ('1'))
    AND (country.iso_code <> '')
    AND (o.total_paid_real > 0)
ORDER BY
    customer.date_add DESC