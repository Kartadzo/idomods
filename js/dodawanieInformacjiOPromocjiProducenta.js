const head = doument.getElementByTagName('head')[0];
const style = document.createElement('style');
style.type = 'text/css';
style.setAttribute('class', 'monit_rabatu');
const css = `
    {
        border: 1px solid red;
        color: red;
        width: -webkit - max - content;
        width: -moz - max - content;
        width: max - content;
        padding: 3px 9px 2px 5px;
        line - height: normal;
        margin: 2px 0 8px;
    }
`;
style.appendChild(document.createTextNode(css));
head.appendChild(style);

const producentPromotion = [
    {
        name: 'Actona',
        producerCode: '1684492499',
        code: 'tophit23',
        value: '13%',
        terminDate: '23-07-2023'
    },
    {
        name: 'Forte',
        producerCode: '5904767140403',
        code: 'tophit23',
        value: '13%',
        terminDate: '23-07-2023'
    },
]

function findProducent(codeToFind) {
    for (let i = 0; i < producentPromotion.length; i++) {
        if (producentPromotion[i].producerCode == codeToFind) {
            return `-${producentPromotion[i].value} z kodem ${producentPromotion[i].code}`
        }
    }
    return '';
}

text = findProducent('[iai:itemcardpage_product_producer_code]')
if (text != '') {
    const elementRabat = document.getElementById('projector_productname')
    const rabat = document.createElement('div');
    rabat.innerHTML = text
    elementRabat.after(rabat)
}



// <script>
// //     const url = new URL(window.location.href);

// // // Sprawdzamy, czy parametr `dev` jest ustawiony na wartość `true`
// // if (url.searchParams.get("dev") === "true") {
//         const array_data = [
//         {
//             producentName:`Krysiak`,
//             code:`decem23`,
//             precentRabate:`10%`,
//             endDate:`31.08.2023`,
//             active:true
//         },
//         {
//             producentName:`Taranko`,
//             code:`decem23`,
//             precentRabate:`10%`,
//             endDate:`31.08.2023`,
//             active:true
//         },
//         {
//             producentName:`relaks`,
//             code:`decem23`,
//             precentRabate:`10%`,
//             endDate:`31.08.2023`,
//             active:true
//         },
//         {
//             producentName:`Meblomax`,
//             code:`decem23`,
//             precentRabate:`10%`,
//             endDate:`31.08.2023`,
//             active:true
//         },
//         {
//             producentName:`eltap`,
//             code:`decem23`,
//             precentRabate:`10%`,
//             endDate:`31.08.2023`,
//             active:true
//         },
//         {
//             producentName:`Mościccy`,
//             code:`decem23`,
//             precentRabate:`10%`,
//             endDate:`31.08.2023`,
//             active:true
//         },
//         {
//             producentName:`MC Akcent`,
//             code:`decem23`,
//             precentRabate:`10%`,
//             endDate:`31.08.2023`,
//             active:true
//         },
//         {
//             producentName:`Mp Nidzica`,
//             code:`decem23`,
//             precentRabate:`10%`,
//             endDate:`31.08.2023`,
//             active:true
//         },
//         {
//             producentName:`Signal`,
//             code:`tophit23`,
//             precentRabate:`5%`,
//             endDate:`31.08.2023`,
//             active:true
//         },
//         {
//             producentName:`king Home`,
//             code:`tophit23`,
//             precentRabate:`5%`,
//             endDate:`31.08.2023`,
//             active:true
//         },
//         {
//             producentName:`Umbra`,
//             code:`tophit23`,
//             precentRabate:`5%`,
//             endDate:`31.08.2023`,
//             active:true
//         },
//         {
//             producentName:`Richmond Interiors`,
//             code:`tophit23`,
//             precentRabate:`5%`,
//             endDate:`31.08.2023`,
//             active:true
//         },
//         {
//             producentName:`Richmond`,
//             code:`tophit23`,
//             precentRabate:`5%`,
//             endDate:`31.08.2023`,
//             active:true
//         },
//         {
//             producentName:`Modesto Design`,
//             code:`tophit23`,
//             precentRabate:`5%`,
//             endDate:`31.08.2023`,
//             active:true
//         },
//         {
//             producentName:`Kare Design`,
//             code:`tophit23`,
//             precentRabate:`5%`,
//             endDate:`31.08.2023`,
//             active:true
//         },
//         {
//             producentName:`Invicta Interior`,
//             code:`tophit23`,
//             precentRabate:`5%`,
//             endDate:`31.08.2023`,
//             active:true
//         },
//         {
//             producentName:`Actona`,
//             code:`tophit23`,
//             precentRabate:`5%`,
//             endDate:`31.08.2023`,
//             active:true
//         },
//         {
//             producentName:`LivinHill`,
//             code:`tophit23`,
//             precentRabate:`5%`,
//             endDate:`31.08.2023`,
//             active:true
//         },
//         {
//             producentName:`Step into Design`,
//             code:`tophit23`,
//             precentRabate:`5%`,
//             endDate:`31.08.2023`,
//             active:true
//         },
//         {
//             producentName:`Forte`,
//             code:`tophit23`,
//             precentRabate:`5%`,
//             endDate:`31.08.2023`,
//             active:true
//         },
//         {
//             producentName:`Katmandu`,
//             code:`tophit23`,
//             precentRabate:`5%`,
//             endDate:`31.08.2023`,
//             active:true
//         },
//         {
//             producentName:`Skandica`,
//             code:`tophit23`,
//             precentRabate:`5%`,
//             endDate:`31.08.2023`,
//             active:true
//         },
//         {
//             producentName:`Louis De Poortere`,
//             code:`tophit23`,
//             precentRabate:`5%`,
//             endDate:`31.08.2023`,
//             active:true
//         },
//         {
//             producentName:`Brink &amp; Campman`,
//             code:`tophit23`,
//             precentRabate:`5%`,
//             endDate:`31.08.2023`,
//             active:true
//         },
//         {
//             producentName:`Wedgwood`,
//             code:`tophit23`,
//             precentRabate:`5%`,
//             endDate:`31.08.2023`,
//             active:true
//         }
        
//     ]

//         const producent_bm = `[iai:product_producer_name]`

//         const find_exists = array_data.find((el)=> el.producentName.trim().toLowerCase() == producent_bm.trim().toLowerCase())
//         if(find_exists){
//             console.log(find_exists)
//             const [dd, mm, rr] = find_exists.endDate.split(".");
//             const date = new Date(rr,mm-1,dd)
//             if(find_exists.active == true &&  date.getTime() > new Date().getTime()){
//                 const _create_el = document.createElement('div')
//                 _create_el.setAttribute('style',`
//                     line-height: 1.125rem;
//                     color: #757575;
//                     padding: 5px 0 15px;
//                    `)
//                                 _create_el.innerHTML = `
//                 <div style="border: 1px solid red;
//                     color: red;
//                     width: -webkit-max-content;
//                     width: -moz-max-content;
//                     width: max-content;
//                     padding: 3px 9px 2px 5px;
//                     line-height: normal;
//                     margin: 2px 0 8px;">-${find_exists.precentRabate} z kodem <strong>${find_exists.code}</strong></div>
//                 Promocja trwa do: <span style="color: #ff1a1a;">${find_exists.endDate}</span>
//                 `
//                 const projector_wrapper = document.getElementById(`projector_prices_wrapper`)
//                 if(projector_wrapper)
//                     projector_wrapper.after(_create_el)
//             }
//         }        
//     // }

// </script>