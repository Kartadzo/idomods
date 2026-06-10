SELECT
  customer.firstname as fn,
  customer.lastname as ln,
  country.iso_code as ct,
  address.postcode as zip,
  address.phone,
  customer.email,
  (
    SELECT
      SUM(total_paid_real / conversion_rate)
    FROM
      pacb_orders o
    WHERE
      (o.id_customer = customer.id_customer)
      AND (o.id_shop IN ('1'))
      AND (o.valid = 1)
  ) as value
FROM
  pacb_customer customer
  LEFT JOIN pacb_address address ON address.id_customer = customer.id_customer
  LEFT JOIN pacb_country country ON country.id_country = address.id_country
WHERE
  (customer.deleted = 0)
  AND (customer.id_shop IN ('1'))
  AND (country.iso_code <> '')
ORDER BY
  customer.date_add DESC

  