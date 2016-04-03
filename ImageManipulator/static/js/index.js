$(document).ready(function() {
    function updateBoxAndFrameOptions() {
        var val = $('#animation-form input[name=animation]:checked').val();
        if (val == 'auto') {
            $('#box-size-form').hide();
            $('#frames-form').hide();
            $('#save-frames-form').show();
        } else if (val == 'one_frame') {
            $('#box-size-form').show();
            $('#frames-form').hide();
            $('#save-frames-form').hide();
        } else {
            $('#box-size-form').show();
            $('#frames-form').show();
            $('#save-frames-form').show();
        }
    }
    $('#animation-form input:radio').click(updateBoxAndFrameOptions);
    updateBoxAndFrameOptions();

    function updateRotationOptions() {
        if ($('#average-form input:checkbox').is(':checked')) {
            $('#rotation > option:nth-child(2)').hide();
            $('#rotation > option:nth-child(3)').hide();
        } else if (!($('#box-shape-form input:radio:checked').val()
            == 'square')) {
            $('#rotation > option:nth-child(2)').show();
            $('#rotation > option:nth-child(3)').hide();
        } else {
            $('#rotation > option:nth-child(2)').show();
            $('#rotation > option:nth-child(3)').show();
        }
    }
    $('#box-shape-form input:radio').click(updateRotationOptions);
    $('#average-form input:checkbox').click(updateRotationOptions);
    updateRotationOptions();
});
