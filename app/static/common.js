var common = (function () {
    var modal;

    return {
        url: function () {
            return $.cookie('base_url');
        },

        // methods
        modal: function (title, body, footerHtml, clsBtn, backDrop, preEvents) {
            clsBtn = clsBtn ? '<button type="button" class="close" data-dismiss="modal" aria-label="Закрыть"><span aria-hidden="true">&times;</span></button>' : '';
            modal = $(
                '<div class="modal fade" tabindex="-1" role="dialog">' +
                '<div class="modal-dialog">' +
                '<div class="modal-content">' +
                '<div class="modal-header">' +
                clsBtn +
                '<h4 class="modal-title">' + title + '</h4>' +
                '</div>' +
                '<div class="modal-body">' +
                body +
                '</div>' +
                '<div class="modal-footer">' +
                footerHtml +
                '</div>' +
                '</div>' +
                '</div>' +
                '</div>'
            );
            if (preEvents) {
                if (preEvents.constructor === Array) {
                    for (var i = 0; i < preEvents.length; i++) {
                        modal.on(preEvents[i]['event'], preEvents[i]['callback']);
                    }
                } else {
                    modal.on(preEvents['event'], preEvents['callback']);
                }
            }
            modal.modal({
                backdrop: backDrop,
                keyboard: clsBtn
            });
            return modal;
        },
        closeModal: function (callback) {
            if(typeof modal != 'undefined')
                modal.modal('hide').on('hidden.bs.modal', function () {
                    if (callback) {
                        callback();
                    }
                    $(this).remove();
                });
        },

        // Escaping string
        escapeStr: function (str) {
            str = str.split('\\').join('\\\\');
            str = str.split(',').join('\\,');
            str = str.split('\"').join('\\\"');
            str = str.split('+').join('\\+');
            str = str.split('=').join('\\=');
            str = str.split('<').join('\\<');
            str = str.split('>').join('\\>');
            str = str.split(';').join('\\;');
            return str;
        },

        /**************************************************************************************************************/

        /**
         * Получение списка устройств
         *
         * @returns {Array}
         */
        getDevices: function (callback)
        {
            //var devices = ucgo.call('getDevices'), result = [];
            //if (devices !== null && devices) {
            //    devices = devices.split(ucgo.row_separator());
            //    for (var i = 0; i < devices.length; i++) {
            //        var device = devices[i].split(ucgo.column_separator()),
            //            neededDevices = ['JavaToken', 'KzToken', 'GammaJaCarta'];
            //        if (neededDevices.indexOf(device[1]) !== -1 && device[2] == 'gost') {
            //            result.push({
            //                reader: device[0],
            //                device: device[1],
            //                algorithm: device[2]
            //            });
            //        }
            //    }
            //}
        }
    }
})();


var column_separator = "|col|";
var row_separator = "|row|";

(function(){

    if (typeof isConnect != 'undefined') {
        if(isConnect == false) {
            //var key = "v0LeLc7QIJKiRrxvWNTmmh7QniHOmCqlMeTfFlgZYK/EROF/NIrktI2GCV0aRbbcoeOzOZNenDx74GKufOcXZQ==";
            //var key = "Ki/QdMbpa5whmkgVt1G9nZAcso7qXjsw1CQ9rn8nvhSBopoU5LnzvO0NPoiGM5290OytlarYkqLCmqcg1KXnWQ==";
            //connectTumSocket1(key, function() {
            //    console.log("Connected");

            //});
		socket = new WebSocket("wss://127.0.0.1:6127/tumarcsp/");
		socket.onopen = function(){
			isConnect = true;
			var options = {
				"apiKey":key
			};
			SetAPIKey(options, function(event) {
				var data = JSON.parse(event.data);
				console.log(data);
				if(data.result == "true") {
					console.log("Connected");
				} else {
					isConnect = false;
					alert("Неверная лицензия CryptoSocket");
				}
			});
		}
		socket.onclose = function(){
			isConnect = false;
		}
		socket.onerror = function(event){
			console.log(event.code);
			console.log(event.reason);
		}
        }
    } else {
        alert('CryptoSocket не запущен');
    }

})();

if (!window.atob) {
    var tableStr = "ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz0123456789+/";
    var table = tableStr.split("");

    window.atob = function (base64) {
        if (/(=[^=]+|={3,})$/.test(base64)) throw new Error("String contains an invalid character");
        base64 = base64.replace(/=/g, "");
        var n = base64.length & 3;
        if (n === 1) throw new Error("String contains an invalid character");
        for (var i = 0, j = 0, len = base64.length / 4, bin = []; i < len; ++i) {
            var a = tableStr.indexOf(base64[j++] || "A"), b = tableStr.indexOf(base64[j++] || "A");
            var c = tableStr.indexOf(base64[j++] || "A"), d = tableStr.indexOf(base64[j++] || "A");
            if ((a | b | c | d) < 0) throw new Error("String contains an invalid character");
            bin[bin.length] = ((a << 2) | (b >> 4)) & 255;
            bin[bin.length] = ((b << 4) | (c >> 2)) & 255;
            bin[bin.length] = ((c << 6) | d) & 255;
        }
        return String.fromCharCode.apply(null, bin).substr(0, bin.length + n - 4);
    };

    window.btoa = function (bin) {
        for (var i = 0, j = 0, len = bin.length / 3, base64 = []; i < len; ++i) {
            var a = bin.charCodeAt(j++), b = bin.charCodeAt(j++), c = bin.charCodeAt(j++);
            if ((a | b | c) > 255) throw new Error("String contains an invalid character");
            base64[base64.length] = table[a >> 2] + table[((a << 4) & 63) | (b >> 4)] +
                (isNaN(b) ? "=" : table[((b << 2) & 63) | (c >> 6)]) +
                (isNaN(b + c) ? "=" : table[c & 63]);
        }
        return base64.join("");
    };

}

function hexToBase64(str) {
    return btoa(String.fromCharCode.apply(null,
        str.replace(/\r|\n/g, "").replace(/([\da-fA-F]{2}) ?/g, "0x$1 ").replace(/ +$/, "").split(" "))
    );
}

function base64ToHex(str) {
    for (var i = 0, bin = atob(str.replace(/[ \r\n]+$/, "")), hex = []; i < bin.length; ++i) {
        var tmp = bin.charCodeAt(i).toString(16);
        if (tmp.length === 1) tmp = "0" + tmp;
        hex[hex.length] = tmp;
    }
    return hex.join(" ");
}

function base64ToArrayBuffer(base64) {
    var binaryString =  window.atob(base64);
    var binaryLen = binaryString.length;
    var bytes = new Uint8Array(binaryLen);
    for (var i = 0; i < binaryLen; i++)        {
        bytes[i] = binaryString.charCodeAt(i);
    }
    return bytes;
}

var saveByteArray = (function () {
    console.log("Сохранение данных");
    var a = document.createElement("a");
    document.body.appendChild(a);
    a.style = "display: none";
    return function (data, name) {
        var blob = new Blob(data, {type: "octet/stream"}),
            url = window.URL.createObjectURL(blob);

        //var origin = window.location.origin;
        //url = url.replace(origin, common.url());

        a.href = url;
        a.download = name;
        a.click();
        setTimeout(function(){
            //a.parentNode.removeChild(a);
            //document.body.removeChild(a);
            window.URL.revokeObjectURL(url);
            console.log("Сохранение данных завершено");
        }, 200);
    };
}());

window.onerror = function(msg, url, linenumber){
	console.log('window.onerror');
	console.log('msg ' + msg);
	console.log('url ' + url);
	console.log('linenumber ' + linenumber);
}