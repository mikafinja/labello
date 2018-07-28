// prevent form to be submitted by clicking on the print button
$("#print").click(function (e) {
    e.preventDefault();
});

function get_mode() {
    var mode = $("#mode:checked").val();
    if (mode === "qrcode") {
        $("#card_label_text").hide();
        $("#card_label_image").hide();
        $("#card_font_format").hide();
        $("#card_label_qrcode").show();
        return "qrcode"
    }
    else if (mode === "image") {
        $("#card_label_qrcode").hide();
        $("#card_label_text").hide();
        $("#card_font_format").hide();
        $("#card_label_image").show();
        return "image"
    } else {
        $("#card_label_qrcode").hide();
        $("#card_label_image").hide();
        $("#card_font_format").show();
        $("#card_label_text").show();
        return "text";
    }
}

function get_data_text() {
    // get font name
    var font_family = $("#font_family").find(":selected").text();

    // get label size
    var label_size = $("#label_size").find(":selected").val();

    // get font size and restrict between 3 and 255
    var font_size = $("#font_size").val();
    if (font_size < 3) {
        font_size = 3;
    }
    else if (font_size > 255) {
        font_size = 255;
    }

    // get font style
    var underline = false;
    if ($("#font_style_underline:checked").val() === "underline") {
        underline = true;
    }

    // get text and change empty text to single whitespace
    var text = $("#label_text").val();
    if (text.length === 0) {
        text = " ";
    }

    // get vertical alignment
    var valign = $("input[name='font-vertical-align']:checked").val();

    // get horizontal alignment
    var halign = $("input[name='font-horizontal-align']:checked").val();

    // get label orientation
    var orientation = $("input[name='label_orientation']:checked").val();

    // create json data object

    var label_data = {
        text: text,
        font_name: font_family,
        font_size: font_size,
        valign: valign,
        halign: halign,
        underline: underline,
        label_size: label_size,
        orientation: orientation,
    };

    return label_data;
}

function get_data_qrcode() {
    // get font family
    var font_family = $("#font_family").find(":selected").text();

    // get label size
    var label_size = $("#label_size").find(":selected").val();

    // get label orientation
    var orientation = $("input[name='label_orientation']:checked").val();

    // get font size and restrict between 3 and 255
    var font_size = $("#font_size").val();
    if (font_size < 3) {
        font_size = 3;
    }
    else if (font_size > 255) {
        font_size = 255;
    }

    // get error correction
    var error_correction = $("#qr_error").find(":selected").val();

    var label_data = {
        font_name: font_family,
        qr_text: $("#qr_text").val(),
        label_size: label_size,
        orientation: orientation,
        font_size: font_size,
        error_correction: error_correction,
    }

    return label_data;
}

function get_data_image() {
    // get label size
    var label_size = $("#label_size").find(":selected").val();

    // get label orientation
    var orientation = $("input[name='label_orientation']:checked").val();

    var fd = new FormData();
    var files = $('#label_image')[0].files[0];
    fd.append('file', files);
    fd.append('label_size', label_size);
    fd.append('orientation', orientation);

    return fd;
}

function preview() {
    // ajax request to get preview image
    if (get_mode() === "text") {
        $.ajax({
            contentType: 'application/json; charset=UTF-8', type: "post", url: "/preview",
            data: JSON.stringify(get_data_text()),
            success: function (result) {
                $('#preview').attr('src', 'data:image/png;base64,' + result);
            }
        });
    }
    if (get_mode() === "qrcode") {
        $.ajax({
            contentType: 'application/json; charset=UTF-8', type: "post", url: "/preview/qrcode",
            data: JSON.stringify(get_data_qrcode()),
            success: function (result) {
                $('#preview').attr('src', 'data:image/png;base64,' + result);
            }
        });
    }
    if (get_mode() === "image") {
        $.ajax({
            enctype: 'multipart/form-data', contentType: false, processData: false, type: "post", url: "/preview/image",
            data: get_data_image(),
            success: function (result) {
                $('#preview').attr('src', 'data:image/png;base64,' + result);
            }
        });
    }
}

function print() {
    $('#status').html('printing...').removeClass("alert-info alert-danger alert-warning alert-success alert-secondary").addClass("alert-info");

    if (get_mode() === "text") {
        $.ajax({
            contentType: 'application/json; charset=UTF-8', type: "post", url: "/print/text",
            data: JSON.stringify(get_data_text()),
            success: function (result) {
                $('#status').html(result[1]).removeClass("alert-info alert-danger alert-warning alert-success alert-secondary").addClass(result[0]);
            },
            error: function (result) {
                $('#status').html(`<b>E R R O R</b>The API threw an error!<b>Status:</b>${result.status}<b>Info:</b>${result.responseText}`).removeClass("alert-info alert-danger alert-warning alert-success").addClass("alert-danger");
                console.warn(`The API returned the status code ${result.status}`);
                console.warn(`The API gave these additional information: ${result.responseText}`);
            }
        });
    } else if (get_mode() === "qrcode") {
        $.ajax({
            contentType: 'application/json; charset=UTF-8', type: "post", url: "/print/qrcode",
            data: JSON.stringify(get_data_qrcode()),
            success: function (result) {
                $('#status').html(result);
            }
        });
    } else if (get_mode() === "image") {
        $.ajax({
            enctype: 'multipart/form-data', contentType: false, processData: false, type: "post", url: "/print/image",
            data: get_data_image(),
            success: function (result) {
                $('#status').html(result);
            }
        });
    }
}

$(document).ready(function () {
    preview();
    $("#label_image").on('change', function () {
        preview();
    });
});

$("#font_family").change(function () {
    preview();
});

$("#label_size").change(function () {
    preview();
});

$("#label_text").keyup(function () {
    preview();
});

$("#font_size").change(function () {
    preview();
});

$("#font_size").keyup(function () {
    preview();
});

$("input[name='font-vertical-align']").change(function () {
    preview();
});

$("input[name='font-horizontal-align']").change(function () {
    preview();
});

$("input[name='label_orientation']").change(function () {
    preview();
});

$("input[name='mode']").change(function () {
    preview();
});

$("#qr_text").keyup(function () {
    preview();
});

$("#qr_error").change(function () {
    preview();
});
