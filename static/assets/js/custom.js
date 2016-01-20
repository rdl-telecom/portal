jQuery(function() {
    var telInput = $(".phone-number");

    var lang = $('[name="lang"]').val();

    // initialise plugin
    telInput.intlTelInput({
        allowExtensions: false,
        autoFormat: true,
        autoPlaceholder: true,
        defaultCountry: lang,
        nationalMode: false,
        preferredCountries: [lang],
        utilsScript: "/assets/js/utils.js"
    });

    // on blur: validate
    telInput.blur(function() {
        if ($.trim(telInput.val())) {
            if (telInput.intlTelInput("isValidNumber")) {
                //validMsg.removeClass("hide");
            } else {
                telInput.addClass("error");
                //errorMsg.removeClass("hide");
                //validMsg.addClass("hide");
            }
        }
    });

    // on keydown: reset
    telInput.keydown(function() {
        telInput.removeClass("error");
    });

    jQuery("#show-confirm-form").click(function(){
        jQuery.showConfrimCode();
        return false;
    });

    jQuery("#confirm").click(function(){
        return false;
    });


    jQuery.showConfrimCode = function(){
        jQuery("#confirm-form").removeClass("hidden");
        jQuery("#login-form").addClass("hidden");

    };

    jQuery.showAgreement = function() {
        $.magnificPopup.open({
            items: {
                src: "#agreement-modal"
            },
            type: "inline",
            closeOnBgClick: false,
            callbacks: {
                open: function() {
                    $("#wrapper").niceScroll({
                        cursorcolor: "#1c469e",
                        cursorwidth: "15px"
                    });
                },
                beforeClose: function() {
                    $("#wrapper").getNiceScroll().remove();
                }
            },
            modal: false,
        }, 0);
    }

    $(".showAgreement").click(function(){
        jQuery.showAgreement();
        return false;
    });
});