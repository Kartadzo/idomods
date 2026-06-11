

// Usuwanie elementu ze strony z użyciem id

// const element = document.querySelector(".projector_shipping_info");//wzór dla class
// const element = document.querySelector("#projector_shipping_info");//wzor dla id
const element = document.getElementById("Progress");
element.remove();
//alternatywa
document.getElementById("Progress").style.display = "none";

// //alternatywa w css
// <style>
//     #projector_shipping_info {
//         display: none!important;
// }
// </style>

pintrk('track', 'checkout', {
    value: {{ Enhanced Transaction Revenue }},
    order_quantity: {{ item.quantity }}
  });

<script>
    pintrk('track', 'pagevisit', {
        promo_code: 'ZIMA10',
    event_id: 'eventId0001',
 });
</script>




//<script>
var array_value_objects = {{ dlv - eventModel.items[]}}

for (var i = 0; i < array_value_objects.length; i++) {
    var contents_format = {}
    contents_format.product_id = array_value_objects[i].item_id              //id
    contents_format.product_quantity = array_value_objects[i].item_quantity  //quantity
    contents_format.product_price = array_value_objects[i].price        //price
    array_ready_objects.push(contents_format)
}

var productIds = array_value_objects.map(function (item) {
    return item.item_id;
});
//</script>
//<script>
pintrk('track', 'checkout', {
    value: {{ dlv - eventModel.value}},
    currency: {{ dlv - eventModel.currency}},
    order_id: {{ dlv - eventModel.transaction_id}},
    order_quantity: array_value_objects.length,
    line_items: array_ready_objects
 });
//</script>
<script>
    pintrk('track', 'AddToCart', {
        product_id: {{ dlv - eventModel.items.0.item_id}},
    product_quantity: {{ dlv - eventModel.items.0.quantity}},
    product_price: {{ dlv - eventModel.value}},
    currency: {{ dlv - eventModel.currency}}
 });
</script>

// Proszę nie realizować zamówienia.