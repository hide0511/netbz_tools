function saveCsvFile(data){

    var now = new Date();
    var csv_file = "netbiztools_" + now.getFullYear() + ("0" + (now.getMonth() + 1)).slice(-2) + ("0" + now.getDate()).slice(-2) + ".csv";
    var bom = new Uint8Array([0xEF, 0xBB, 0xBF]);

    var blob = new Blob([bom, data], {"type": "text/plain"});

    var a = jQuery("<a></a>", {href: window.URL.createObjectURL(blob),
            download: csv_file,
            target: "_blank"})[0];
    if (window.navigator.msSaveBlob) {
        window.navigator.msSaveBlob(blob, csv_file); 
        window.navigator.msSaveOrOpenBlob(blob, csv_file);
    } else if (window.URL && window.URL.createObjectURL) {
        document.body.appendChild(a);
        a.click();
        document.body.removeChild(a);
    } else if (window.webkitURL && window.webkitURL.createObject) {
        a.click();
    } else {
        window.open('data:text/csv;charset=utf-16;' + ';base64,' + window.Base64.encode($('#resultTextArea').val()), '_blank');
    }
}
