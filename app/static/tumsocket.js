var socket;
var isConnect = false;
function errorConnectDefault(data) { alert(data);}
var errorConnectCallBack = errorConnectDefault;
function connectTumSocket() {
    socket = new WebSocket("wss://localhost:6127/tumarcsp/");
    socket.onopen = function(){
        isConnect = true;
    }
    socket.onclose = function(){
        isConnect = false;
    }
    socket.onerror = function(event){
        console.log(event);
    }
}
function connectTumSocket1(apiKey, callback) {
    socket = new WebSocket("wss://localhost:6127/tumarcsp/");
    socket.onopen = function(){
        isConnect = true;
        var options = {
            "apiKey":apiKey
        };
        SetAPIKey(options, callback);
    }
    socket.onclose = function(){
        isConnect = false;
    }
    socket.onerror = function(event){
        console.log(event);
    }
}
function connectTumSocket2(apiKey, callback, errorCallBack, onOpenCallBack, onErrorCallBack, onCloseCallBack) {
    socket = new WebSocket("wss://localhost:6127/tumarcsp/");
    socket.onopen = function(){
        isConnect = true;
        var options = {
            "apiKey":apiKey
        };
        SetAPIKey(options, callback);
        onOpenCallBack();
    }
    socket.onclose = function(){
        isConnect = false;
        onCloseCallBack();
    }
    socket.onerror = function(event){
        console.log(event);
        onErrorCallBack();
    }
    errorConnectCallBack = errorCallBack;
}
function GetProfInfo(options, callback){
    var param = {
        "TumarCSP": "BaseAPI",
        "Function": "GetProfInfo",
        "Param": {
            "profile":options.profile,
            "id":options.id,
            "pass":options.pass,
        }
    };
    if (!isConnect) {
        errorConnectCallBack("CryptoSocket not avaible");
        return null;
    }
    socket.onmessage = callback;
    socket.send(JSON.stringify(param));
}
var GetProfInfoReturn={};
function Sign(options, callback){
    var param = {
        "TumarCSP": "BaseAPI",
        "Function": "Sign",
        "Param": {
            "profile":options.profile,
            "pass":options.pass,
            "sn":options.sn,
            "detach":options.detach,
            "isConvert":options.isConvert,
            "isCert":options.isCert,
            "data":options.data,
            "hashType":options.hashType,
            "hash":options.hash,
            "showSN":options.showSN,
            "transID":options.transID,
            "cert":options.cert,
            "id":options.id,
            "ocsp":options.ocsp,
            "tsp":options.tsp,
            "signattr":options.signattr,
            "unsignattr":options.unsignattr,
            "pkcs7":options.pkcs7,
        }
    };
    if (!isConnect) {
        errorConnectCallBack("CryptoSocket not avaible");
        return null;
    }
    socket.onmessage = callback;
    socket.send(JSON.stringify(param));
}
var SignReturn={};
function GetAllKeys(options, callback){
    var param = {
        "TumarCSP": "BaseAPI",
        "Function": "GetAllKeys",
        "Param": {
            "id":options.id,
            "url":options.url,
        }
    };
    if (!isConnect) {
        errorConnectCallBack("CryptoSocket not avaible");
        return null;
    }
    socket.onmessage = callback;
    socket.send(JSON.stringify(param));
}
var GetAllKeysReturn={};
function CreatePKCS10(options, callback){
    var param = {
        "TumarCSP": "BaseAPI",
        "Function": "CreatePKCS10",
        "Param": {
            "profile":options.profile,
            "pass":options.pass,
            "dn":options.dn,
            "templ":options.templ,
            "isExport":options.isExport,
            "genNew":options.genNew,
            "keyType":options.keyType,
            "keySize":options.keySize,
            "isAltName":options.isAltName,
            "hashType":options.hashType,
            "altEmail":options.altEmail,
            "altDN":options.altDN,
            "altURI":options.altURI,
            "altREGID":options.altREGID,
            "altIP":options.altIP,
            "id":options.id,
            "contName":options.contName,
        }
    };
    if (!isConnect) {
        errorConnectCallBack("CryptoSocket not avaible");
        return null;
    }
    socket.onmessage = callback;
    socket.send(JSON.stringify(param));
}
var CreatePKCS10Return={};
function CreateCertificateRequest(options, callback){
    var param = {
        "TumarCSP": "BaseAPI",
        "Function": "CreateCertificateRequest",
        "Param": {
            "PKCS10":{
                "profile":options.PKCS10.profile,
                "pass":options.PKCS10.pass,
                "dn":options.PKCS10.dn,
                "templ":options.PKCS10.templ,
                "isExport":options.PKCS10.isExport,
                "genNew":options.PKCS10.genNew,
                "keyType":options.PKCS10.keyType,
                "keySize":options.PKCS10.keySize,
                "isAltName":options.PKCS10.isAltName,
                "hashType":options.PKCS10.hashType,
                "altEmail":options.PKCS10.altEmail,
                "altDN":options.PKCS10.altDN,
                "altURI":options.PKCS10.altURI,
                "altREGID":options.PKCS10.altREGID,
                "altIP":options.PKCS10.altIP,
                "id":options.PKCS10.id,
                "contName":options.PKCS10.contName,
            },
            "PKCS7":{
                "profile":options.PKCS7.profile,
                "pass":options.PKCS7.pass,
                "sn":options.PKCS7.sn,
                "isCert":options.PKCS7.isCert,
                "hashType":options.PKCS7.hashType,
                "showSN":options.PKCS7.showSN,
                "transID":options.PKCS7.transID,
                "cert":options.PKCS7.cert,
            }
        }
    };
    if (!isConnect) {
        errorConnectCallBack("CryptoSocket not avaible");
        return null;
    }
    socket.onmessage = callback;
    socket.send(JSON.stringify(param));
}
var CreateCertificateRequestReturn={};
function InstallCertificate(options, callback){
    var param = {
        "TumarCSP": "BaseAPI",
        "Function": "InstallCertificate",
        "Param": {
            "profile":options.profile,
            "pass":options.pass,
            "certificate":options.certificate,
            "flagCN":options.flagCN,
            "rootCertificate":options.rootCertificate,
            "id":options.id,
        }
    };
    if (!isConnect) {
        errorConnectCallBack("CryptoSocket not avaible");
        return null;
    }
    socket.onmessage = callback;
    socket.send(JSON.stringify(param));
}
var InstallCertificateReturn={};
function GetTransactionID(options, callback){
    var param = {
        "TumarCSP": "BaseAPI",
        "Function": "GetTransactionID",
        "Param": {
            "id":options.id,
        }
    };
    if (!isConnect) {
        errorConnectCallBack("CryptoSocket not avaible");
        return null;
    }
    socket.onmessage = callback;
    socket.send(JSON.stringify(param));
}
var GetTransactionIDReturn={};
function GetAllCertificate(options, callback){
    var param = {
        "TumarCSP": "BaseAPI",
        "Function": "GetAllCertificate",
        "Param": {
            "id":options.id,
        }
    };
    if (!isConnect) {
        errorConnectCallBack("CryptoSocket not avaible");
        return null;
    }
    socket.onmessage = callback;
    socket.send(JSON.stringify(param));
}
var GetAllCertificateReturn={};
function LoadKeyFromFile(options, callback){
    var param = {
        "TumarCSP": "BaseAPI",
        "Function": "LoadKeyFromFile",
        "Param": {
            "id":options.id,
            "pathKey":options.pathKey,
            "pass":options.pass,
        }
    };
    if (!isConnect) {
        errorConnectCallBack("CryptoSocket not avaible");
        return null;
    }
    socket.onmessage = callback;
    socket.send(JSON.stringify(param));
}
var LoadKeyFromFileReturn={};
function LoadKeyFromProfile(options, callback){
    var param = {
        "TumarCSP": "BaseAPI",
        "Function": "LoadKeyFromProfile",
        "Param": {
            "id":options.id,
            "profile":options.profile,
            "pass":options.pass,
        }
    };
    if (!isConnect) {
        errorConnectCallBack("CryptoSocket not avaible");
        return null;
    }
    socket.onmessage = callback;
    socket.send(JSON.stringify(param));
}
var LoadKeyFromProfileReturn={};
function LoadKeyFromTokens(options, callback){
    var param = {
        "TumarCSP": "BaseAPI",
        "Function": "LoadKeyFromTokens",
        "Param": {
            "id":options.id,
            "plugin_name":options.plugin_name,
            "pass":options.pass,
        }
    };
    if (!isConnect) {
        errorConnectCallBack("CryptoSocket not avaible");
        return null;
    }
    socket.onmessage = callback;
    socket.send(JSON.stringify(param));
}
var LoadKeyFromTokensReturn={};
function initialRegistrationRequest(options, callback){
    var param = {
        "TumarCSP": "BaseAPI",
        "Function": "initialRegistrationRequest",
        "Param": {
            "id":options.id,
            "profile":options.profile,
            "pass":options.pass,
            "uid":options.uid,
            "secret":options.secret,
            "keyOID":options.keyOID,
            "altEmail":options.altEmail,
            "altDN":options.altDN,
            "altURI":options.altURI,
            "altREGID":options.altREGID,
            "altIP":options.altIP,
        }
    };
    if (!isConnect) {
        errorConnectCallBack("CryptoSocket not avaible");
        return null;
    }
    socket.onmessage = callback;
    socket.send(JSON.stringify(param));
}
var initialRegistrationRequestReturn={};
function initialRegistrationResponse(options, callback){
    var param = {
        "TumarCSP": "BaseAPI",
        "Function": "initialRegistrationResponse",
        "Param": {
            "id":options.id,
            "profile":options.profile,
            "pass":options.pass,
            "secret":options.secret,
            "irresp":options.irresp,
        }
    };
    if (!isConnect) {
        errorConnectCallBack("CryptoSocket not avaible");
        return null;
    }
    socket.onmessage = callback;
    socket.send(JSON.stringify(param));
}
var initialRegistrationResponseReturn={};
function pollingRequest(options, callback){
    var param = {
        "TumarCSP": "BaseAPI",
        "Function": "pollingRequest",
        "Param": {
            "id":options.id,
            "profile":options.profile,
            "pass":options.pass,
            "transactionId":options.transactionId,
            "genOid":options.genOid,
            "cert":options.cert,
            "uid":options.uid,
            "secret":options.secret,
        }
    };
    if (!isConnect) {
        errorConnectCallBack("CryptoSocket not avaible");
        return null;
    }
    socket.onmessage = callback;
    socket.send(JSON.stringify(param));
}
var pollingRequestReturn={};
function pollingResponse(options, callback){
    var param = {
        "TumarCSP": "BaseAPI",
        "Function": "pollingResponse",
        "Param": {
            "id":options.id,
            "profile":options.profile,
            "pass":options.pass,
            "secret":options.secret,
            "processResponse":options.processResponse,
            "iresp":options.iresp,
        }
    };
    if (!isConnect) {
        errorConnectCallBack("CryptoSocket not avaible");
        return null;
    }
    socket.onmessage = callback;
    socket.send(JSON.stringify(param));
}
var pollingResponseReturn={};
function createOCSPRequest(options, callback){
    var param = {
        "TumarCSP": "BaseAPI",
        "Function": "createOCSPRequest",
        "Param": {
            "id":options.id,
            "profile":options.profile,
            "cert":options.cert,
        }
    };
    if (!isConnect) {
        errorConnectCallBack("CryptoSocket not avaible");
        return null;
    }
    socket.onmessage = callback;
    socket.send(JSON.stringify(param));
}
var createOCSPRequestReturn={};
function parseOCSPResponce(options, callback){
    var param = {
        "TumarCSP": "BaseAPI",
        "Function": "parseOCSPResponce",
        "Param": {
            "id":options.id,
            "resp":options.resp,
        }
    };
    if (!isConnect) {
        errorConnectCallBack("CryptoSocket not avaible");
        return null;
    }
    socket.onmessage = callback;
    socket.send(JSON.stringify(param));
}
var parseOCSPResponceReturn={};
function certificationRequest(options, callback){
    var param = {
        "TumarCSP": "BaseAPI",
        "Function": "certificationRequest",
        "Param": {
            "id":options.id,
            "profile":options.profile,
            "pass":options.pass,
            "keyOID":options.keyOID,
            "altEmail":options.altEmail,
            "altDN":options.altDN,
            "altURI":options.altURI,
            "altREGID":options.altREGID,
            "altIP":options.altIP,
        }
    };
    if (!isConnect) {
        errorConnectCallBack("CryptoSocket not avaible");
        return null;
    }
    socket.onmessage = callback;
    socket.send(JSON.stringify(param));
}
var certificationRequestReturn={};
function transactionListRequest(options, callback){
    var param = {
        "TumarCSP": "BaseAPI",
        "Function": "transactionListRequest",
        "Param": {
            "id":options.id,
            "profile":options.profile,
            "pass":options.pass,
            "cert":options.cert,
        }
    };
    if (!isConnect) {
        errorConnectCallBack("CryptoSocket not avaible");
        return null;
    }
    socket.onmessage = callback;
    socket.send(JSON.stringify(param));
}
var transactionListRequestReturn={};
function transactionListResponse(options, callback){
    var param = {
        "TumarCSP": "BaseAPI",
        "Function": "transactionListResponse",
        "Param": {
            "id":options.id,
            "profile":options.profile,
            "pass":options.pass,
            "trresp":options.trresp,
        }
    };
    if (!isConnect) {
        errorConnectCallBack("CryptoSocket not avaible");
        return null;
    }
    socket.onmessage = callback;
    socket.send(JSON.stringify(param));
}
var transactionListResponseReturn={};
function createSecretRequest(options, callback){
    var param = {
        "TumarCSP": "BaseAPI",
        "Function": "createSecretRequest",
        "Param": {
            "id":options.id,
            "profile":options.profile,
            "pass":options.pass,
            "serverCert":options.serverCert,
            "type":options.type,
            "uid":options.uid,
            "secret":options.secret,
            "dn":options.dn,
            "state":options.state,
        }
    };
    if (!isConnect) {
        errorConnectCallBack("CryptoSocket not avaible");
        return null;
    }
    socket.onmessage = callback;
    socket.send(JSON.stringify(param));
}
var createSecretRequestReturn={};
function createSecretResponse(options, callback){
    var param = {
        "TumarCSP": "BaseAPI",
        "Function": "createSecretResponse",
        "Param": {
            "id":options.id,
            "profile":options.profile,
            "pass":options.pass,
            "resp":options.resp,
        }
    };
    if (!isConnect) {
        errorConnectCallBack("CryptoSocket not avaible");
        return null;
    }
    socket.onmessage = callback;
    socket.send(JSON.stringify(param));
}
var createSecretResponseReturn={};
function x509ObjectRequest(options, callback){
    var param = {
        "TumarCSP": "BaseAPI",
        "Function": "x509ObjectRequest",
        "Param": {
            "id":options.id,
            "profile":options.profile,
            "pass":options.pass,
            "cert":options.cert,
            "crl":options.crl,
        }
    };
    if (!isConnect) {
        errorConnectCallBack("CryptoSocket not avaible");
        return null;
    }
    socket.onmessage = callback;
    socket.send(JSON.stringify(param));
}
var x509ObjectRequestReturn={};
function x509objectResponse(options, callback){
    var param = {
        "TumarCSP": "BaseAPI",
        "Function": "x509objectResponse",
        "Param": {
            "id":options.id,
            "profile":options.profile,
            "pass":options.pass,
            "resp":options.resp,
            "crl":options.crl,
        }
    };
    if (!isConnect) {
        errorConnectCallBack("CryptoSocket not avaible");
        return null;
    }
    socket.onmessage = callback;
    socket.send(JSON.stringify(param));
}
var x509objectResponseReturn={};
function depositionRequest(options, callback){
    var param = {
        "TumarCSP": "BaseAPI",
        "Function": "depositionRequest",
        "Param": {
            "id":options.id,
            "profile":options.profile,
            "pass":options.pass,
            "uid":options.uid,
            "userPassword":options.userPassword,
            "transactionId":options.transactionId,
            "cert":options.cert,
        }
    };
    if (!isConnect) {
        errorConnectCallBack("CryptoSocket not avaible");
        return null;
    }
    socket.onmessage = callback;
    socket.send(JSON.stringify(param));
}
var depositionRequestReturn={};
function depositionResponse(options, callback){
    var param = {
        "TumarCSP": "BaseAPI",
        "Function": "depositionResponse",
        "Param": {
            "id":options.id,
            "profile":options.profile,
            "pass":options.pass,
            "userPassword":options.userPassword,
            "otp":options.otp,
            "resp":options.resp,
        }
    };
    if (!isConnect) {
        errorConnectCallBack("CryptoSocket not avaible");
        return null;
    }
    socket.onmessage = callback;
    socket.send(JSON.stringify(param));
}
var depositionResponseReturn={};
function certificateConfirmationRequest(options, callback){
    var param = {
        "TumarCSP": "BaseAPI",
        "Function": "certificateConfirmationRequest",
        "Param": {
            "id":options.id,
            "profile":options.profile,
            "pass":options.pass,
            "pollingResponse":options.pollingResponse,
            "confirm":options.confirm,
            "cert":options.cert,
        }
    };
    if (!isConnect) {
        errorConnectCallBack("CryptoSocket not avaible");
        return null;
    }
    socket.onmessage = callback;
    socket.send(JSON.stringify(param));
}
var certificateConfirmationRequestReturn={};
function certificateConfirmationResponse(options, callback){
    var param = {
        "TumarCSP": "BaseAPI",
        "Function": "certificateConfirmationResponse",
        "Param": {
            "id":options.id,
            "profile":options.profile,
            "pass":options.pass,
            "resp":options.resp,
        }
    };
    if (!isConnect) {
        errorConnectCallBack("CryptoSocket not avaible");
        return null;
    }
    socket.onmessage = callback;
    socket.send(JSON.stringify(param));
}
var certificateConfirmationResponseReturn={};
function revocationRequest(options, callback){
    var param = {
        "TumarCSP": "BaseAPI",
        "Function": "revocationRequest",
        "Param": {
            "id":options.id,
            "profile":options.profile,
            "pass":options.pass,
            "sn":options.sn,
            "userCertificate":options.userCertificate,
            "reason":options.reason,
            "uid":options.uid,
            "userPassword":options.userPassword,
            "serverCert":options.serverCert,
        }
    };
    if (!isConnect) {
        errorConnectCallBack("CryptoSocket not avaible");
        return null;
    }
    socket.onmessage = callback;
    socket.send(JSON.stringify(param));
}
var revocationRequestReturn={};
function revocationResponse(options, callback){
    var param = {
        "TumarCSP": "BaseAPI",
        "Function": "revocationResponse",
        "Param": {
            "id":options.id,
            "profile":options.profile,
            "pass":options.pass,
            "resp":options.resp,
        }
    };
    if (!isConnect) {
        errorConnectCallBack("CryptoSocket not avaible");
        return null;
    }
    socket.onmessage = callback;
    socket.send(JSON.stringify(param));
}
var revocationResponseReturn={};
function getIdCardInfo(options, callback){
    var param = {
        "TumarCSP": "BaseAPI",
        "Function": "getIdCardInfo",
        "Param": {
        }
    };
    if (!isConnect) {
        errorConnectCallBack("CryptoSocket not avaible");
        return null;
    }
    socket.onmessage = callback;
    socket.send(JSON.stringify(param));
}
var getIdCardInfoReturn={};
function CreateEnvelopedPKCS7(options, callback){
    var param = {
        "TumarCSP": "BaseAPI",
        "Function": "CreateEnvelopedPKCS7",
        "Param": {
            "profile":options.profile,
            "pass":options.pass,
            "id":options.id,
            "algId":options.algId,
            "Flags":options.Flags,
            "data":options.data,
            "isConvert":options.isConvert,
            "RecipCerts":options.RecipCerts,
        }
    };
    if (!isConnect) {
        errorConnectCallBack("CryptoSocket not avaible");
        return null;
    }
    socket.onmessage = callback;
    socket.send(JSON.stringify(param));
}
var CreateEnvelopedPKCS7Return={};
function LoadProfileFromTokens(options, callback){
    var param = {
        "TumarCSP": "BaseAPI",
        "Function": "LoadProfileFromTokens",
        "Param": {
            "id":options.id,
            "plugin_name":options.plugin_name,
        }
    };
    if (!isConnect) {
        errorConnectCallBack("CryptoSocket not avaible");
        return null;
    }
    socket.onmessage = callback;
    socket.send(JSON.stringify(param));
}
var LoadProfileFromTokensReturn={};
function VerifyPKCS7(options, callback){
    var param = {
        "TumarCSP": "BaseAPI",
        "Function": "VerifyPKCS7",
        "Param": {
            "isConvert":options.isConvert,
            "data":options.data,
            "hashType":options.hashType,
            "cert":options.cert,
            "sign":options.sign,
            "id":options.id,
        }
    };
    if (!isConnect) {
        errorConnectCallBack("CryptoSocket not avaible");
        return null;
    }
    socket.onmessage = callback;
    socket.send(JSON.stringify(param));
}
var VerifyPKCS7Return={};
function DecryptEnvelopedPKCS7(options, callback){
    var param = {
        "TumarCSP": "BaseAPI",
        "Function": "DecryptEnvelopedPKCS7",
        "Param": {
            "profile":options.profile,
            "pass":options.pass,
            "id":options.id,
            "data":options.data,
            "isConvert":options.isConvert,
            "isElGamal":options.isElGamal,
            "SenderCert":options.SenderCert,
        }
    };
    if (!isConnect) {
        errorConnectCallBack("CryptoSocket not avaible");
        return null;
    }
    socket.onmessage = callback;
    socket.send(JSON.stringify(param));
}
var DecryptEnvelopedPKCS7Return={};
function DelKey(options, callback){
    var param = {
        "TumarCSP": "BaseAPI",
        "Function": "DelKey",
        "Param": {
            "profile":options.profile,
            "pass":options.pass,
            "sn":options.sn,
            "id":options.id,
        }
    };
    if (!isConnect) {
        errorConnectCallBack("CryptoSocket not avaible");
        return null;
    }
    socket.onmessage = callback;
    socket.send(JSON.stringify(param));
}
var DelKeyReturn={};
function NativeSign(options, callback){
    var param = {
        "TumarCSP": "BaseAPI",
        "Function": "NativeSign",
        "Param": {
            "profile":options.profile,
            "pass":options.pass,
            "sn":options.sn,
            "id":options.id,
            "data":options.data,
            "hash":options.hash,
            "isConvert":options.isConvert,
            "hashType":options.hashType,
        }
    };
    if (!isConnect) {
        errorConnectCallBack("CryptoSocket not avaible");
        return null;
    }
    socket.onmessage = callback;
    socket.send(JSON.stringify(param));
}
var NativeSignReturn={};
function VerifyNative(options, callback){
    var param = {
        "TumarCSP": "BaseAPI",
        "Function": "VerifyNative",
        "Param": {
            "isConvert":options.isConvert,
            "data":options.data,
            "hash":options.hash,
            "hashType":options.hashType,
            "cert":options.cert,
            "sign":options.sign,
            "id":options.id,
        }
    };
    if (!isConnect) {
        errorConnectCallBack("CryptoSocket not avaible");
        return null;
    }
    socket.onmessage = callback;
    socket.send(JSON.stringify(param));
}
var VerifyNativeReturn={};
function LoadKeyFromBlob(options, callback){
    var param = {
        "TumarCSP": "BaseAPI",
        "Function": "LoadKeyFromBlob",
        "Param": {
            "id":options.id,
            "blob":options.blob,
            "pass":options.pass,
            "session_id":options.session_id,
        }
    };
    if (!isConnect) {
        errorConnectCallBack("CryptoSocket not avaible");
        return null;
    }
    socket.onmessage = callback;
    socket.send(JSON.stringify(param));
}
var LoadKeyFromBlobReturn={};
function CreateHash(options, callback){
    var param = {
        "TumarCSP": "BaseAPI",
        "Function": "CreateHash",
        "Param": {
            "id":options.id,
            "blob":options.blob,
            "isConvert":options.isConvert,
            "algID":options.algID,
            "format":options.format,
            "alf":options.alf,
        }
    };
    if (!isConnect) {
        errorConnectCallBack("CryptoSocket not avaible");
        return null;
    }
    socket.onmessage = callback;
    socket.send(JSON.stringify(param));
}
var CreateHashReturn={};
function NativeCrypt(options, callback){
    var param = {
        "TumarCSP": "BaseAPI",
        "Function": "NativeCrypt",
        "Param": {
            "isCrypt":options.isCrypt,
            "secret":options.secret,
            "hashType":options.hashType,
            "isConvert":options.isConvert,
            "useSalt":options.useSalt,
            "filename":options.filename,
            "salt":options.salt,
            "id":options.id,
            "data":options.data,
        }
    };
    if (!isConnect) {
        errorConnectCallBack("CryptoSocket not avaible");
        return null;
    }
    socket.onmessage = callback;
    socket.send(JSON.stringify(param));
}
var NativeCryptReturn={};
function CheckCertificate(options, callback){
    var param = {
        "TumarCSP": "BaseAPI",
        "Function": "CheckCertificate",
        "Param": {
            "certificate":options.certificate,
            "rootCertificate":options.rootCertificate,
            "id":options.id,
        }
    };
    if (!isConnect) {
        errorConnectCallBack("CryptoSocket not avaible");
        return null;
    }
    socket.onmessage = callback;
    socket.send(JSON.stringify(param));
}
var CheckCertificateReturn={};
function createTSPRequest(options, callback){
    var param = {
        "TumarCSP": "BaseAPI",
        "Function": "createTSPRequest",
        "Param": {
            "id":options.id,
            "hashType":options.hashType,
            "data":options.data,
            "isConvert":options.isConvert,
            "policy":options.policy,
            "includeServerCert":options.includeServerCert,
        }
    };
    if (!isConnect) {
        errorConnectCallBack("CryptoSocket not avaible");
        return null;
    }
    socket.onmessage = callback;
    socket.send(JSON.stringify(param));
}
var createTSPRequestReturn={};
function SignXML(options, callback){
    var param = {
        "TumarCSP": "XMLAPI",
        "Function": "SignXML",
        "Param": {
            "profile":options.profile,
            "pass":options.pass,
            "sn":options.sn,
            "keyOid":options.keyOid,
            "nsPref":options.nsPref,
            "xml":options.xml,
        }
    };
    if (!isConnect) {
        errorConnectCallBack("CryptoSocket not avaible");
        return null;
    }
    socket.onmessage = callback;
    socket.send(JSON.stringify(param));
}
var SignXMLReturn={};
function VerifyXML(options, callback){
    var param = {
        "TumarCSP": "XMLAPI",
        "Function": "VerifyXML",
        "Param": {
            "xml":options.xml,
        }
    };
    if (!isConnect) {
        errorConnectCallBack("CryptoSocket not avaible");
        return null;
    }
    socket.onmessage = callback;
    socket.send(JSON.stringify(param));
}
var VerifyXMLReturn={};
function SignSOAPXML(options, callback){
    var param = {
        "TumarCSP": "XMLAPI",
        "Function": "SignSOAPXML",
        "Param": {
            "profile":options.profile,
            "pass":options.pass,
            "sn":options.sn,
            "keyOid":options.keyOid,
            "idElement":options.idElement,
            "xml":options.xml,
        }
    };
    if (!isConnect) {
        errorConnectCallBack("CryptoSocket not avaible");
        return null;
    }
    socket.onmessage = callback;
    socket.send(JSON.stringify(param));
}
var SignSOAPXMLReturn={};
function CheckAPIKey(options, callback){
    var param = {
        "TumarCSP": "SYSAPI",
        "Function": "CheckAPIKey",
        "Param": {
            "apiKey":options.apiKey,
        }
    };
    if (!isConnect) {
        errorConnectCallBack("CryptoSocket not avaible");
        return null;
    }
    socket.onmessage = callback;
    socket.send(JSON.stringify(param));
}
var CheckAPIKeyReturn={};
function SetAPIKey(options, callback){
    var param = {
        "TumarCSP": "SYSAPI",
        "Function": "SetAPIKey",
        "Param": {
            "apiKey":options.apiKey,
        }
    };
    if (!isConnect) {
        errorConnectCallBack("CryptoSocket not avaible");
        return null;
    }
    socket.onmessage = callback;
    socket.send(JSON.stringify(param));
}
var SetAPIKeyReturn={};
function SendRequest(options, callback){
    var param = {
        "TumarCSP": "SYSAPI",
        "Function": "SendRequest",
        "Param": {
            "request":options.request,
            "address":options.address,
            "port":options.port,
        }
    };
    if (!isConnect) {
        errorConnectCallBack("CryptoSocket not avaible");
        return null;
    }
    socket.onmessage = callback;
    socket.send(JSON.stringify(param));
}
var SendRequestReturn={};
function CheckUpdate(options, callback){
    var param = {
        "TumarCSP": "SYSAPI",
        "Function": "CheckUpdate",
        "Param": {
            "address":options.address,
            "port":options.port,
            "product_code":options.product_code,
        }
    };
    if (!isConnect) {
        errorConnectCallBack("CryptoSocket not avaible");
        return null;
    }
    socket.onmessage = callback;
    socket.send(JSON.stringify(param));
}
var CheckUpdateReturn={};
function Update(options, callback){
    var param = {
        "TumarCSP": "SYSAPI",
        "Function": "Update",
        "Param": {
            "address":options.address,
            "port":options.port,
            "url":options.url,
        }
    };
    if (!isConnect) {
        errorConnectCallBack("CryptoSocket not avaible");
        return null;
    }
    socket.onmessage = callback;
    socket.send(JSON.stringify(param));
}
var UpdateReturn={};
function GetFingerprint(options, callback){
    var param = {
        "TumarCSP": "SYSAPI",
        "Function": "GetFingerprint",
        "Param": {
            "timeout":options.timeout,
            "viewdlg":options.viewdlg,
        }
    };
    if (!isConnect) {
        errorConnectCallBack("CryptoSocket not avaible");
        return null;
    }
    socket.onmessage = callback;
    socket.send(JSON.stringify(param));
}
var GetFingerprintReturn={};
function CheckFingerprint(options, callback){
    var param = {
        "TumarCSP": "SYSAPI",
        "Function": "CheckFingerprint",
        "Param": {
            "timeout":options.timeout,
            "viewdlg":options.viewdlg,
            "fingerprint":options.fingerprint,
        }
    };
    if (!isConnect) {
        errorConnectCallBack("CryptoSocket not avaible");
        return null;
    }
    socket.onmessage = callback;
    socket.send(JSON.stringify(param));
}
var CheckFingerprintReturn={};
function InstallFingerprintToken(options, callback){
    var param = {
        "TumarCSP": "SYSAPI",
        "Function": "InstallFingerprintToken",
        "Param": {
            "pin":options.pin,
            "name":options.name,
            "indx":options.indx,
            "timeout":options.timeout,
            "viewdlg":options.viewdlg,
        }
    };
    if (!isConnect) {
        errorConnectCallBack("CryptoSocket not avaible");
        return null;
    }
    socket.onmessage = callback;
    socket.send(JSON.stringify(param));
}
var InstallFingerprintTokenReturn={};
function CheckFingerprintFromToken(options, callback){
    var param = {
        "TumarCSP": "SYSAPI",
        "Function": "CheckFingerprintFromToken",
        "Param": {
            "timeout":options.timeout,
            "viewdlg":options.viewdlg,
            "pin":options.pin,
            "name":options.name,
            "indx":options.indx,
        }
    };
    if (!isConnect) {
        errorConnectCallBack("CryptoSocket not avaible");
        return null;
    }
    socket.onmessage = callback;
    socket.send(JSON.stringify(param));
}
var CheckFingerprintFromTokenReturn={};
function GetMACAddress(options, callback){
    var param = {
        "TumarCSP": "SYSAPI",
        "Function": "GetMACAddress",
        "Param": {
            "id":options.id,
        }
    };
    if (!isConnect) {
        errorConnectCallBack("CryptoSocket not avaible");
        return null;
    }
    socket.onmessage = callback;
    socket.send(JSON.stringify(param));
}
var GetMACAddressReturn={};
function CryptMessage(options, callback){
    var param = {
        "TumarCSP": "ASNAPI",
        "Function": "CryptMessage",
        "Param": {
            "profile":options.profile,
            "pass":options.pass,
            "id":options.id,
            "dataDescriptor":options.dataDescriptor,
            "dataOID":options.dataOID,
            "cryptOID":options.cryptOID,
            "ownerCertificate":options.ownerCertificate,
            "Flags":options.Flags,
            "data":options.data,
            "isConvert":options.isConvert,
            "RecipCerts":options.RecipCerts,
        }
    };
    if (!isConnect) {
        errorConnectCallBack("CryptoSocket not avaible");
        return null;
    }
    socket.onmessage = callback;
    socket.send(JSON.stringify(param));
}
var CryptMessageReturn={};
function DecryptMessage(options, callback){
    var param = {
        "TumarCSP": "ASNAPI",
        "Function": "DecryptMessage",
        "Param": {
            "profile":options.profile,
            "pass":options.pass,
            "id":options.id,
            "data":options.data,
            "ownerCertificate":options.ownerCertificate,
            "isConvert":options.isConvert,
            "isElGamal":options.isElGamal,
            "SenderCerts":options.SenderCerts,
        }
    };
    if (!isConnect) {
        errorConnectCallBack("CryptoSocket not avaible");
        return null;
    }
    socket.onmessage = callback;
    socket.send(JSON.stringify(param));
}
var DecryptMessageReturn={};
function ShowInfoMessage(options, callback){
    var param = {
        "TumarCSP": "ASNAPI",
        "Function": "ShowInfoMessage",
        "Param": {
            "id":options.id,
            "data":options.data,
            "isConvert":options.isConvert,
        }
    };
    if (!isConnect) {
        errorConnectCallBack("CryptoSocket not avaible");
        return null;
    }
    socket.onmessage = callback;
    socket.send(JSON.stringify(param));
}
var ShowInfoMessageReturn={};
function ShowInfoPKCS10(options, callback){
    var param = {
        "TumarCSP": "ASNAPI",
        "Function": "ShowInfoPKCS10",
        "Param": {
            "id":options.id,
            "data":options.data,
        }
    };
    if (!isConnect) {
        errorConnectCallBack("CryptoSocket not avaible");
        return null;
    }
    socket.onmessage = callback;
    socket.send(JSON.stringify(param));
}
var ShowInfoPKCS10Return={};
function ShowInfoCertificate(options, callback){
    var param = {
        "TumarCSP": "ASNAPI",
        "Function": "ShowInfoCertificate",
        "Param": {
            "id":options.id,
            "data":options.data,
        }
    };
    if (!isConnect) {
        errorConnectCallBack("CryptoSocket not avaible");
        return null;
    }
    socket.onmessage = callback;
    socket.send(JSON.stringify(param));
}
var ShowInfoCertificateReturn={};
function ShowOpenDialog(options, callback){
    var param = {
        "TumarCSP": "FORMAPI",
        "Function": "ShowOpenDialog",
        "Param": {
            "title":options.title,
        }
    };
    if (!isConnect) {
        errorConnectCallBack("CryptoSocket not avaible");
        return null;
    }
    socket.onmessage = callback;
    socket.send(JSON.stringify(param));
}
var ShowOpenDialogReturn={};
