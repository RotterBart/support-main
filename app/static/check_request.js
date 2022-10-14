$(function () {
    /**
     * Валидация формы нескольких устройств
     *
     * @param submitHandler
     */
    var validateDevicesForm = function (submitHandler) {
        $('#frm-several-devices').validate({
            rules: {
                'devices': 'required'
            },
            messages: {
                'devices': 'Выберите устройство'
            },
            errorPlacement: function (er, el) {
                el.parent().addClass('has-error');
                er.addClass('help-block').insertAfter(el);
            },
            success: function (er, el) {
                er.parent().removeClass('has-error').addClass('has-success');
                er.remove();
            },
            submitHandler: submitHandler
        });
    };
    /**
     * Валидация формы выбора ключевой пары для проверки
     *
     * @param submitHandler
     */
    var validateKeyPairsForm = function (submitHandler) {
        $('#frm-key-pairs').validate({
            rules: {
                'key-pairs': 'required'
            },
            messages: {
                'key-pairs': 'Выберите ключевую пару'
            },
            errorPlacement: function (er, el) {
                el.parent().addClass('has-error');
                er.addClass('help-block').insertAfter(el);
            },
            success: function (er, el) {
                er.parent().removeClass('has-error').addClass('has-success');
                er.remove();
            },
            submitHandler: submitHandler
        });
    };
    /**
     * Валидация пароля для устройства
     *
     * @param submitHandler
     */
    var validateDevicePassword = function (submitHandler) {
        $('#frm-device-password').validate({
            rules: {
                'device-password': 'required'
            },
            messages: {
                'device-password': 'Введите пароль'
            },
            onfocusin: function(element) {
                $(element).valid();
            },
            errorPlacement: function (er, el) {
                el.parent().addClass('has-error');
                er.addClass('help-block').insertAfter(el);
            },
            success: function (er, el) {
                er.parent().removeClass('has-error').addClass('has-success');
                er.remove();
            },
            submitHandler: submitHandler
        });
    };

    /**
     * Выбор устройств
     *
     * @param devices
     */
    var selectDevices = function (devices) {
        var readers = [];
        for (var i = 0; i < devices.length; i++) {
            readers.push(devices[i]['reader']);
        }

        common.modal('Выберите устройство', 'Загрузка...', '', false, 'static').on('shown.bs.modal', function (e) {
            $('div.modal-body').load(base_url + '/several-devices-form', 'readers=' + JSON.stringify(readers), function () {
                $('#slct-devices').focus();

                validateDevicesForm(function (form) {
                    common.closeModal(function () {
                        var reader = $('#slct-devices').val();
                        var device = getDeviceFromReader(reader, devices);
                        getKeyPairs(device);
                    });
                });

                $('#btn-cancel-device-select').click(function (e) {
                    common.closeModal(function () {
                        $('#div-check-device').addClass('hidden').siblings('div').addClass('hidden');
                    });
                });
            });
        });
    };

    /**
     * Получение токена по названию Reader из списка токенов
     *
     * @param reader
     * @param devices
     */
    var getDeviceFromReader = function (reader, devices) {
        for (var i = 0; i < devices.length; i++) {
            if (devices[i].reader == reader) {
                return devices[i];
            }
        }
        return null;
    };

    /**
     * Получение ключевой пары
     *
     * @param device
     */
    var getKeyPairs = function (device) {
        $('#div-check-key-pairs').removeClass('hidden');

        setTimeout(function () {

            var profile = device.profile;

            GetAllKeys({url: profile}, function (event) {
                var data = JSON.parse(event.data);
                if (data.result == "true") {

                    var keyPairsHolder = [];

                    if (data.response.profiles) {
                        if (Object.keys(data.response.profiles).length) {
                            for (var key in data.response.profiles[profile]) {
                                iter = data.response.profiles[profile][key];
                                if (!iter.certificateBlob) {
                                    iter.publicKey = hexToBase64(iter.publicKey);
                                    keyPairsHolder.push({
                                        'objectName': iter.serialNum,
                                        'keyAlgId': iter.algID,
                                        'keyAlgString': iter.algID, // TODO ?
                                        'publicKey': iter.publicKey
                                    });
                                }
                            }
                        }
                    }

                    if (keyPairsHolder.length) {
                        $('#div-check-key-pairs .success-information').removeClass('hidden').siblings('div').addClass('hidden');
                        if (keyPairsHolder.length > 1) {
                            common.modal('Выберите проверяемый ключ', 'Загрузка...', '', false, 'static').on('shown.bs.modal', function (e) {
                                $('div.modal-body').load(base_url + '/key-pairs-form', {'key_pairs': keyPairsHolder}, function () {
                                    $('#slct-key-pairs').focus().change(function (e) {
                                        // Информация о выбранной ключевой паре
                                        var val = $(this).val();
                                        if (val !== '') {
                                            $('#div-key-pair-info').removeClass('hidden');

                                            var keyPair = keyPairsHolder[parseInt(val)],
                                                keyAlgId = keyPair['keyAlgId'] == 10810 ? 'Подпись' : 'Ключевой обмен',
                                                keyAlgString = keyPair['keyAlgId'] == 10810 ? 'ГОСТ 34.310-2004' : 'Неизвестно';

                                            $('#div-key-pair-info .form-group:eq(0) p').text(keyAlgString);
                                            $('#div-key-pair-info .form-group:eq(1) p').text(keyAlgId);

                                        } else {
                                            $('#div-key-pair-info .form-group p').text('');
                                            $('#div-key-pair-info').addClass('hidden');
                                        }
                                    });

                                    validateKeyPairsForm(function () {
                                        common.closeModal(function () {
                                            var keyPair = keyPairsHolder[parseInt($('#slct-key-pairs').val())];
                                            checkKeyPairs(device, keyPair['objectName'], keyPair['publicKey']);
                                        });
                                    });

                                    $('#btn-cancel-choose-certificate').click(function () {
                                        common.closeModal(function () {
                                            $('#div-check-key-pairs').addClass('hidden').siblings('div').addClass('hidden');
                                        });
                                    });
                                });
                            });
                        } else {
                            checkKeyPairs(device, keyPairsHolder[0]['objectName'], keyPairsHolder[0]['publicKey']);
                        }
                    } else {
                        $('#div-check-key-pairs .fail-information').removeClass('hidden').siblings('div').addClass('hidden');
                    }

                } else {
                    alert('Недействительный профиль');
                }
            });
        }, 50);
    };

    var checkKeyPairs = function (device, objectName, publicKey) {
        $('#div-request-server').removeClass('hidden');
        $.post(base_url + '/check-request', {'public_key': publicKey}).done(function (r) {
            var status = r['status'];
            if (status === 1 || status === 2) {
                common.modal('Введите пароль от устройства', 'Загрузка...', '', false, 'static').on('shown.bs.modal', function (e) {
                    $('div.modal-body').load(base_url + '/device-password-form', function () {
                        
                        var passwordField = $('#inpt-device-password');
                        passwordField.focus();
                        // Валидация формы ввода пароля на устройство
                        validateDevicePassword(function (form) {
                            $('#inpt-try-password-device').val('Подождите...').prop('disabled', true);
                            var password = passwordField.val(),
                                validator = this;

                            setTimeout(function () {
                                if (status === 1) {
                                    var certBody = r['data'];
                                    InstallCertificate({
                                        profile: device.profile,
                                        pass: password,
                                        certificate: certBody
                                    }, function (event) {
                                        var data = JSON.parse(event.data);
                                        if (data.result == "true") {

                                            ShowInfoCertificate({data: certBody}, function (event) {
                                                var data = JSON.parse(event.data);
                                                if (data.result == "true") {
                                                    common.closeModal(function () {
                                                        var dn = data.Subject;
                                                        var confirmedInfo = $('#div-request-server .confirmed-information');
                                                        confirmedInfo.removeClass('hidden').siblings('div').addClass('hidden');
                                                        confirmedInfo.find('span.success-text').html('Запрос подтвержден и сертификат <strong>' + dn + '</strong> успешно установлен');
                                                    });
                                                }
                                            });

                                        } else {
                                            validator.showErrors({
                                                'device-password': 'Пароль не совпадает! Пожалуйста, попробуйте еще раз'
                                            });
                                            $('#inpt-try-password-device').val('Далее').prop('disabled', false);
                                            console.log("Код ошибки " + data.code);
                                            console.log("Описание ошибки " + data.error);
                                        }
                                    });

                                } else if (status === 2) {

                                    DelKey({
                                        profile: device.profile,
                                        pass: password,
                                        sn: objectName
                                    }, function (event) {
                                        var data = JSON.parse(event.data);
                                        if (data.result == "true") {
                                            common.closeModal(function () {
                                                var rejectedInfo = $('#div-request-server .rejected-information');
                                                rejectedInfo.removeClass('hidden').siblings('div').addClass('hidden');
                                                rejectedInfo.find('span.rejected-text').text('Ваш запрос отклонен и ключевые пары были успешно удалены. Причина отклонения: ' + r['data']);
                                            });
                                        } else {
                                            validator.showErrors({
                                                'device-password': 'Пароль не совпадает! Пожалуйста, попробуйте еще раз'
                                            });
                                            $('#inpt-try-password-device').val('Далее').prop('disabled', false);
                                        }
                                    });
                                }
                            }, 50);
                        });

                        $('#btn-cancel-device-password').click(function (e) {
                            common.closeModal(function () {
                                $('#div-check-device').addClass('hidden').siblings('div').addClass('hidden');
                            });
                        });
                    });
                });
            } else {
                $('#div-request-server .processing-information').removeClass('hidden').siblings('div').addClass('hidden');
            }
        }).fail(function () {
            $('#div-request-server .fail-information').removeClass('hidden').siblings('div').addClass('hidden');
        });
    };

    /**
     * Проверка устройств
     */
    var checkDevices = function () {
        LoadProfileFromTokens({plugin_name: "newoids"}, function (event) {
            $('#div-check-device').removeClass('hidden').siblings('div').each(function () {
                $(this).addClass('hidden');
                $(this).find('.information').removeClass('hidden').siblings('div').addClass('hidden');
            });
            var data = JSON.parse(event.data);
            var devices = [];

            if (data.result == "true") {
                for (var key in data.response) {
                    devices.push({
                        profile: data.response[key].profile,
                        reader: data.response[key].reader
                    });
                }

                if (devices.length) {
                    if (devices.length > 1) {
                        selectDevices(devices);
                    } else {
                        getKeyPairs(devices[0]);
                    }
                    $('#div-check-device .success-information').removeClass('hidden').siblings('div').addClass('hidden');
                } else {
                    setTimeout(checkDevices, 250);
                    $('#div-check-device .fail-information').removeClass('hidden').siblings('div').addClass('hidden');
                }
            } else {
                setTimeout(checkDevices, 250);
                $('#div-check-device .fail-information').removeClass('hidden').siblings('div').addClass('hidden');
            }
        });
    };

    $('#btn-check-request').click(function (e) {
        checkDevices();
    });
});